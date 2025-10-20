import gradio as gr
import pandas as pd
import json
import os
import time
import threading
from database import CharacterDatabase
from file_manager import CharacterFileManager
import numpy as np
import soundfile as sf
import zipfile
from tqdm import tqdm
from action_parameters import ALL_ACTION_PARAMS
from dialogue_generation_ui_v2 import build_dialogue_generation_ui
from voice_pack_exporter import VoicePackExporter

# 应用JSON Schema补丁以避免Gradio内部错误
import gradio_client.utils
original_json_schema_to_python_type = gradio_client.utils.json_schema_to_python_type

def patched_json_schema_to_python_type(schema):
    """修复Gradio JSON schema处理中的bool类型错误"""
    try:
        # 如果schema是bool类型，直接返回str
        if isinstance(schema, bool):
            return str
        # 如果schema不是字典，返回str
        if not isinstance(schema, dict):
            return str
        return original_json_schema_to_python_type(schema)
    except (TypeError, AttributeError):
        return str

# 应用补丁
gradio_client.utils.json_schema_to_python_type = patched_json_schema_to_python_type

# Initialize database and file manager
db = CharacterDatabase()
file_manager = CharacterFileManager()

def get_language_encoding(language):
    """获取语言编码映射"""
    language_map = {
        "中文": "台词",
        "English": "英文台词", 
        "日本語": "日文台词"
    }
    return language_map.get(language, "台词")

def create_initial_df(dialogue_column):
    """创建初始DataFrame，包含所有动作参数"""
    try:
        # 创建包含所有动作参数的DataFrame，使用字符串类型避免bool类型问题
        initial_data = [["☐", str(param), "等待生成..."] for param in ALL_ACTION_PARAMS]
        df = pd.DataFrame(initial_data, columns=["选择", "动作参数", dialogue_column])
        
        # 强制确保数据类型为字符串，避免JSON schema问题
        df["选择"] = df["选择"].astype(str)
        df["动作参数"] = df["动作参数"].astype(str).fillna('')
        df[dialogue_column] = df[dialogue_column].astype(str).fillna('')
        
        print(f"Created initial DataFrame with {len(df)} rows")
        print(f"DataFrame dtypes: {df.dtypes}")
        
        return df
    except Exception as e:
        print(f"Error creating initial DataFrame: {e}")
        # 回退为空表
        df = pd.DataFrame(columns=["选择", "动作参数", dialogue_column])
        df = df.astype({"选择": str, "动作参数": str, dialogue_column: str})
        return df

# Character Management Functions
def create_character(name, description, avatar_file):
    # 输入验证 - 角色名称和描述为必填项
    if not name or not name.strip():
        return "角色名称不能为空。"
    
    if not description or not description.strip():
        return "角色描述不能为空。"
    
    # 清理输入，移除前后空格
    name = name.strip()
    description = description.strip()
    
    # 检查角色名称长度
    if len(name) > 50:
        return "角色名称不能超过50个字符。"
    
    # 检查角色是否已存在
    existing_characters = db.get_characters()
    for char in existing_characters:
        if char[1].lower() == name.lower():
            return f"角色 '{name}' 已存在，请使用不同的名称。"
    
    # 验证描述长度 - 根据功能需求调整为50000字符
    if len(description) > 50000:
        return "角色描述不能超过50000个字符。"
    
    try:
        # 创建角色目录结构
        character_path = file_manager.create_character_directory(name)
        
        # 处理头像文件（选填项）
        avatar_path = None
        thumbnail_path = None
        if avatar_file is not None:
            # gr.File组件返回的是文件路径字符串或文件对象
            if isinstance(avatar_file, str):
                # 如果是文件路径字符串，需要创建临时文件对象
                import tempfile
                import shutil
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(avatar_file)[1])
                shutil.copy2(avatar_file, temp_file.name)
                temp_file.close()
                
                # 创建一个简单的文件对象模拟
                class TempFileObj:
                    def __init__(self, path):
                        self.name = os.path.basename(path)
                        self.path = path
                    
                    def read(self):
                        with open(self.path, 'rb') as f:
                            return f.read()
                
                avatar_file_obj = TempFileObj(temp_file.name)
                original_path, thumbnail_path = file_manager.save_character_avatar(name, avatar_file_obj)
                # 清理临时文件
                os.unlink(temp_file.name)
            else:
                # 如果是文件对象，直接使用
                original_path, thumbnail_path = file_manager.save_character_avatar(name, avatar_file)
            
            avatar_path = thumbnail_path if thumbnail_path else original_path
        
        # 保存角色描述
        file_manager.save_character_description(name, description)
        
        # 在数据库中创建角色记录
        character_id = db.create_character(name, description, avatar_path)
        
        return f"角色 '{name}' 创建成功！目录结构已建立。"
    except Exception as e:
        return f"创建角色失败: {str(e)}"

def update_character_list():
    characters = db.get_characters()
    # 返回HTML格式的头像和角色名称
    result = []
    for character in characters:
        character_id, name = character[0], character[1]
        # 使用文件管理器获取头像路径
        avatar_path = file_manager.get_character_avatar_path(name)
        
        if avatar_path and os.path.exists(avatar_path):
            # 创建HTML img标签显示头像
            avatar_html = f'<img src="file://{avatar_path}" style="width:50px;height:50px;object-fit:cover;border-radius:4px;" alt="Avatar">'
        else:
            # 使用默认头像图标
            avatar_html = '<div style="width:50px;height:50px;background-color:#e0e0e0;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:20px;">👤</div>'
        result.append([avatar_html, name])
    return result

def get_characters_for_update():
    characters = db.get_characters()
    return gr.update(choices=[(character[1], character[0]) for character in characters])

def update_character_fields(character_id):
    character = db.get_character(character_id)
    if character:
        character_id, name = character[0], character[1]
        # 从文件系统读取描述
        description = file_manager.get_character_description(name) or ""
        # 获取头像路径
        avatar_path = file_manager.get_character_avatar_path(name)
        return name, description, avatar_path
    return "", "", None

def update_character(character_id, name, description, avatar_file):
    if not character_id:
        return "更新角色失败：缺少角色ID。"
    
    # 输入验证 - 角色名称和描述为必填项
    if not name or not name.strip():
        return "角色名称不能为空。"
    
    if not description or not description.strip():
        return "角色描述不能为空。"
    
    # 清理输入，移除前后空格
    name = name.strip()
    description = description.strip()
    
    # 检查角色名称长度
    if len(name) > 50:
        return "角色名称不能超过50个字符。"
    
    # 验证描述长度 - 根据功能需求调整为50000字符
    if len(description) > 50000:
        return "角色描述不能超过50000个字符。"
    
    try:
        # 获取原角色信息
        old_character = db.get_character(character_id)
        old_name = old_character[1] if old_character else None
        
        # 检查新名称是否与其他角色冲突（排除当前角色）
        existing_characters = db.get_characters()
        for char in existing_characters:
            if char[0] != character_id and char[1].lower() == name.lower():
                return f"角色名称 '{name}' 已被其他角色使用，请使用不同的名称。"
        
        # 如果名称改变，需要重命名目录
        if old_name and old_name != name:
            old_path = os.path.join(file_manager.base_path, old_name)
            new_path = os.path.join(file_manager.base_path, name)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
        
        # 确保目录存在
        file_manager.create_character_directory(name)
        
        # 处理头像文件（选填项）
        avatar_path = None
        if avatar_file is not None:
            # gr.File组件返回的是文件路径字符串或文件对象
            if isinstance(avatar_file, str):
                # 如果是文件路径字符串，需要创建临时文件对象
                import tempfile
                import shutil
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(avatar_file)[1])
                shutil.copy2(avatar_file, temp_file.name)
                temp_file.close()
                
                # 创建一个简单的文件对象模拟
                class TempFileObj:
                    def __init__(self, path):
                        self.name = os.path.basename(path)
                        self.path = path
                    
                    def read(self):
                        with open(self.path, 'rb') as f:
                            return f.read()
                
                avatar_file_obj = TempFileObj(temp_file.name)
                original_path, thumbnail_path = file_manager.save_character_avatar(name, avatar_file_obj)
                # 清理临时文件
                os.unlink(temp_file.name)
                avatar_path = thumbnail_path if thumbnail_path else original_path
            else:
                # 如果是文件对象，直接使用
                original_path, thumbnail_path = file_manager.save_character_avatar(name, avatar_file)
                avatar_path = thumbnail_path if thumbnail_path else original_path
        else:
            # 保持原有头像
            avatar_path = file_manager.get_character_avatar_path(name)
        
        # 保存角色描述
        file_manager.save_character_description(name, description)
        
        # 更新数据库
        db.update_character(character_id, name, description, avatar_path)
        
        return f"角色 '{name}' 更新成功！"
    except Exception as e:
        return f"更新角色失败: {str(e)}"

# 全局变量用于管理选择状态
# 角色管理相关的全局变量已移除，使用简化的下拉菜单方式

# 角色管理相关的复杂函数已移除，使用简化的下拉菜单方式

def character_ui():
    with gr.Blocks() as character_ui_block:
        gr.Markdown("## 第一步：角色管理")
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 创建角色")
                character_name = gr.Textbox(label="角色名称")
                character_description = gr.Textbox(label="角色描述", lines=3)
                character_avatar = gr.File(label="角色头像", file_types=["image"])
                create_button = gr.Button("创建角色", variant="primary")
                creation_status = gr.Textbox(label="状态", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### 删除角色")
                character_dropdown = gr.Dropdown(
                    label="选择要删除的角色",
                    choices=[],
                    interactive=True
                )
                delete_button = gr.Button("删除角色", variant="stop")
                delete_status = gr.Textbox(label="删除状态", interactive=False)

        # 事件绑定
        def refresh_character_dropdown():
            """刷新角色下拉菜单"""
            characters = db.get_characters()
            choices = [(char[1], char[1]) for char in characters]  # (显示名, 值)
            return gr.Dropdown(choices=choices)

        def delete_character_by_name(character_name):
            """根据角色名删除角色"""
            if not character_name:
                return "请先选择要删除的角色", gr.Dropdown()
            
            try:
                # 获取角色信息
                characters = db.get_characters()
                character_to_delete = None
                for char in characters:
                    if char[1] == character_name:  # char[1] 是角色名
                        character_to_delete = char
                        break
                
                if not character_to_delete:
                    return f"未找到角色: {character_name}", refresh_character_dropdown()
                
                character_id = character_to_delete[0]
                
                # 删除文件系统中的角色目录
                import shutil
                character_dir = f"/Users/Saga/breathVOICE/Characters/{character_name}"
                if os.path.exists(character_dir):
                    shutil.rmtree(character_dir)
                
                # 删除数据库记录
                db.delete_character(character_id)
                
                return f"已成功删除角色: {character_name}", refresh_character_dropdown()
                
            except Exception as e:
                return f"删除角色失败: {str(e)}", refresh_character_dropdown()

        # 创建角色事件
        create_button.click(
            create_character, 
            [character_name, character_description, character_avatar], 
            creation_status
        ).then(
            refresh_character_dropdown,
            outputs=character_dropdown
        )
        
        # 删除角色事件
        delete_button.click(
            delete_character_by_name,
            inputs=character_dropdown,
            outputs=[delete_status, character_dropdown]
        )

        # 页面加载时刷新下拉菜单
        character_ui_block.load(
            refresh_character_dropdown,
            outputs=character_dropdown
        )

    return character_ui_block

def llm_config_ui():
    with gr.Blocks() as llm_config_interface:
        gr.Markdown("## 第二步：LLM配置")
        
        # 页面顶部的三个输入框和两个按钮
        with gr.Row():
            url_input = gr.Textbox(label="API地址", placeholder="https://api.openai.com/v1")
            key_input = gr.Textbox(label="API密钥", type="password")
            model_dropdown = gr.Dropdown(label="选择模型", choices=[])
        
        with gr.Row():
            fetch_models_button = gr.Button("获取模型")
            test_button = gr.Button("测试可用性")
        
        # 状态显示
        status_output = gr.Textbox(label="状态", interactive=False)
        
        # API Configurations 部分
        gr.Markdown("### API配置")
        with gr.Row():
            config_dropdown = gr.Dropdown(label="API配置", choices=["None"], value="None")
            new_button = gr.Button("新建")
            save_button = gr.Button("保存", interactive=False)
            edit_button = gr.Button("编辑", interactive=False)
            delete_button = gr.Button("删除", interactive=False)

        # 隐藏的弹窗组件
        with gr.Column(visible=False) as new_config_modal:
            gr.Markdown("### 新建配置")
            new_config_name = gr.Textbox(label="配置名称")
            with gr.Row():
                save_new_button = gr.Button("保存")
                cancel_new_button = gr.Button("取消")
        
        with gr.Column(visible=False) as edit_config_modal:
            gr.Markdown("### 编辑配置")
            edit_config_name = gr.Textbox(label="配置名称")
            edit_api_url = gr.Textbox(label="API地址", interactive=False)
            edit_api_key = gr.Textbox(label="API密钥", interactive=False, type="password")
            edit_model = gr.Textbox(label="选择模型", interactive=False)
            with gr.Row():
                save_edit_button = gr.Button("保存")
                cancel_edit_button = gr.Button("取消")
        
        with gr.Column(visible=False) as delete_config_modal:
             gr.Markdown("### 删除确认")
             delete_confirm_text = gr.Markdown("")
             with gr.Row():
                 confirm_delete_button = gr.Button("删除")
                 cancel_delete_button = gr.Button("取消")

        # 功能函数
        def update_config_dropdown():
            configs = db.get_llm_configs()
            config_names = [config[1] for config in configs] if configs else []
            choices = ["None"] + config_names
            return gr.update(choices=choices)

        # 辅助函数：按名称查找配置与ID
        def _find_llm_config_by_name(config_name):
            if not config_name or config_name == "None":
                return None
            try:
                configs = db.get_llm_configs()
                for cfg in configs:
                    if cfg[1] == config_name:
                        return cfg  # (id, name, base_url, api_key, model, system_prompt, user_prompt_template, generation_params)
                return None
            except Exception:
                return None

        def _get_llm_config_id_by_name(config_name):
            cfg = _find_llm_config_by_name(config_name)
            return cfg[0] if cfg else None

        def fetch_models(url, api_key):
            if not url or not api_key:
                return gr.update(choices=[]), "API URL and Key are required."
            if not url.endswith('/v1'):
                return gr.update(choices=[]), "URL must end with '/v1'"
            try:
                import openai
                client = openai.OpenAI(base_url=url, api_key=api_key)
                models = client.models.list()
                model_ids = sorted([model.id for model in models.data], key=lambda s: s.lower())
                return gr.update(choices=model_ids), "Models fetched successfully!"
            except Exception as e:
                return gr.update(choices=[]), f"Error: {e}"

        def test_availability(url, api_key, model):
            if not url or not api_key or not model:
                return "URL, API Key, and Model are required to test."
            try:
                import openai
                client = openai.OpenAI(base_url=url, api_key=api_key)
                client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}]
                )
                return "Model is available!"
            except Exception as e:
                return f"Error: {e}"

        def update_button_states(selected_config):
            if selected_config == "None":
                return gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)
            else:
                return gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True)

        def load_config_data(selected_config):
            if selected_config == "None":
                return "", "", gr.update(choices=[])
            cfg = _find_llm_config_by_name(selected_config)
            if cfg:
                base_url = cfg[2] or ""
                api_key = cfg[3] or ""
                model = cfg[4] or ""
                if model:
                    return base_url, api_key, gr.update(choices=[model], value=model)
                else:
                    return base_url, api_key, gr.update(choices=[])
            return "", "", gr.update(choices=[])

        # 事件绑定
        llm_config_interface.load(update_config_dropdown, None, config_dropdown)
        fetch_models_button.click(fetch_models, [url_input, key_input], [model_dropdown, status_output])
        test_button.click(test_availability, [url_input, key_input, model_dropdown], status_output)
        config_dropdown.change(update_button_states, config_dropdown, [save_button, edit_button, delete_button])
        config_dropdown.change(load_config_data, config_dropdown, [url_input, key_input, model_dropdown])

        # 弹窗功能函数
        def show_new_modal():
            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

        def hide_new_modal():
            return gr.update(visible=False), ""

        def save_new_config(name, url, api_key, model):
            if not name or not url or not api_key or not model:
                return gr.update(visible=True), "所有字段都是必填的。"
            try:
                db.add_llm_config(name, url, api_key, model, '', '', '{}')
                return gr.update(visible=False), f"配置 '{name}' 已保存。", update_config_dropdown()
            except Exception as e:
                return gr.update(visible=True), f"保存失败: {e}"

        def show_edit_modal(selected_config):
            if selected_config == "None":
                return gr.update(visible=False), "", "", "", ""
            cfg = _find_llm_config_by_name(selected_config)
            if cfg:
                return gr.update(visible=True), cfg[1], (cfg[2] or ""), (cfg[3] or ""), (cfg[4] or "")
            return gr.update(visible=False), "", "", "", ""

        def hide_edit_modal():
            return gr.update(visible=False)

        def save_edit_config(old_name, new_name, url, api_key, model):
            if not new_name:
                return gr.update(visible=True), "配置名称不能为空。"
            try:
                cfg = _find_llm_config_by_name(old_name)
                if not cfg:
                    return gr.update(visible=True), "未找到原配置。"
                config_id = cfg[0]
                system_prompt = cfg[5] if len(cfg) > 5 else ''
                user_prompt_template = cfg[6] if len(cfg) > 6 else ''
                generation_params = cfg[7] if len(cfg) > 7 else '{}'
                base_url = url or (cfg[2] or '')
                api_key_val = api_key or (cfg[3] or '')
                model_val = model or (cfg[4] or '')
                db.update_llm_config(config_id, new_name, base_url, api_key_val, model_val, system_prompt, user_prompt_template, generation_params)
                return gr.update(visible=False), f"配置已更新为 '{new_name}'。", update_config_dropdown()
            except Exception as e:
                return gr.update(visible=True), f"更新失败: {e}"

        def show_delete_modal(selected_config):
            if selected_config == "None":
                return gr.update(visible=False), ""
            return gr.update(visible=True), f"确定要删除配置 '{selected_config}' 吗？"

        def hide_delete_modal():
            return gr.update(visible=False)

        def confirm_delete_config(selected_config):
            try:
                config_id = _get_llm_config_id_by_name(selected_config)
                if not config_id:
                    return gr.update(visible=True), "未找到配置。"
                db.delete_llm_config(config_id)
                return gr.update(visible=False), f"配置 '{selected_config}' 已删除。", update_config_dropdown(), gr.update(value="None")
            except Exception as e:
                return gr.update(visible=True), f"删除失败: {e}"

        def save_current_config(selected_config, url, api_key, model):
            if selected_config == "None":
                return "请先选择一个配置。"
            if not url or not api_key or not model:
                return "URL、API Key 和 Model 都是必填的。"
            try:
                cfg = _find_llm_config_by_name(selected_config)
                if not cfg:
                    return "未找到配置。"
                config_id = cfg[0]
                system_prompt = cfg[5] if len(cfg) > 5 else ''
                user_prompt_template = cfg[6] if len(cfg) > 6 else ''
                generation_params = cfg[7] if len(cfg) > 7 else '{}'
                db.update_llm_config(config_id, cfg[1], url, api_key, model, system_prompt, user_prompt_template, generation_params)
                return f"配置 '{selected_config}' 已更新。"
            except Exception as e:
                return f"保存失败: {e}"

        # 弹窗事件绑定
        new_button.click(show_new_modal, None, [new_config_modal, edit_config_modal, delete_config_modal])
        cancel_new_button.click(hide_new_modal, None, [new_config_modal, new_config_name])
        save_new_button.click(save_new_config, [new_config_name, url_input, key_input, model_dropdown], [new_config_modal, status_output, config_dropdown])

        edit_button.click(show_edit_modal, config_dropdown, [edit_config_modal, edit_config_name, edit_api_url, edit_api_key, edit_model])
        cancel_edit_button.click(hide_edit_modal, None, edit_config_modal)
        save_edit_button.click(save_edit_config, [config_dropdown, edit_config_name, edit_api_url, edit_api_key, edit_model], [edit_config_modal, status_output, config_dropdown])

        delete_button.click(show_delete_modal, config_dropdown, [delete_config_modal, delete_confirm_text])
        cancel_delete_button.click(hide_delete_modal, None, delete_config_modal)
        confirm_delete_button.click(confirm_delete_config, config_dropdown, [delete_config_modal, status_output, config_dropdown])

        save_button.click(save_current_config, [config_dropdown, url_input, key_input, model_dropdown], status_output)

    return llm_config_interface

def get_character_csv_files(character_name):
    """获取指定角色的CSV文件列表"""
    char_dir = os.path.join("characters", character_name)
    if not os.path.exists(char_dir):
        return []
    return [f for f in os.listdir(char_dir) if f.endswith('.csv')]

def load_csv_file(character_name, filename):
    """加载指定的CSV文件到DataFrame"""
    filepath = os.path.join("characters", character_name, filename)
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            # 确保'选择'列存在
            if '选择' not in df.columns:
                df.insert(0, '选择', 'False')
            else:
                # Ensure boolean-like values are strings
                df['选择'] = df['选择'].astype(str)
            
            # 强制确保动作参数列是字符串类型，防止nan问题
            if '动作参数' in df.columns:
                df['动作参数'] = df['动作参数'].astype(str).fillna('')
            
            # 确保所有台词列都是字符串类型
            for col in df.columns:
                if col not in ['选择', '动作参数']:
                    df[col] = df[col].astype(str).fillna('')
            
            return df
        except Exception as e:
            return f"Error loading file: {e}"
    return "File not found."

def save_current_dialogue(character_name, df_data, custom_filename=None):
    """保存当前对话到CSV文件"""
    if df_data is None:
        return "No data to save."
    
    char_dir = os.path.join("characters", character_name)
    os.makedirs(char_dir, exist_ok=True)
    
    df = pd.DataFrame(df_data)
    
    if custom_filename:
        filename = f"{custom_filename}.csv" if not custom_filename.endswith('.csv') else custom_filename
    else:
        # 寻找一个可用的自动文件名
        i = 1
        while True:
            filename = f"dialogues_{i}.csv"
            if not os.path.exists(os.path.join(char_dir, filename)):
                break
            i += 1
            
    filepath = os.path.join(char_dir, filename)
    df.to_csv(filepath, index=False)
    return f"Successfully saved to {filename}"

def auto_save_dialogue_csv(character_name, df_data):
    """自动保存对话到带有时间戳的CSV文件"""
    if df_data is None:
        return None
        
    char_dir = os.path.join("characters", character_name, "auto_saves")
    os.makedirs(char_dir, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"autosave_{timestamp}.csv"
    filepath = os.path.join(char_dir, filename)
    
    try:
        df = pd.DataFrame(df_data)
        df.to_csv(filepath, index=False)
        return filename
    except Exception as e:
        print(f"Auto-save failed: {e}")
        return None

def import_external_csv(character_name, file_obj):
    """导入外部CSV文件"""
    if file_obj is None:
        return "No file uploaded.", pd.DataFrame()

    char_dir = os.path.join("characters", character_name)
    os.makedirs(char_dir, exist_ok=True)
    
    # 使用原始文件名
    filename = os.path.basename(file_obj.name)
    filepath = os.path.join(char_dir, filename)
    
    # 读取上传的文件内容并保存
    with open(file_obj.name, 'rb') as f_in, open(filepath, 'wb') as f_out:
        f_out.write(f_in.read())
        
    # 加载刚保存的文件
    df = load_csv_file(character_name, filename)
    if isinstance(df, pd.DataFrame):
        return f"Successfully imported and loaded {filename}", df
    else:
        return f"Failed to load the imported file: {df}", pd.DataFrame()

def dialogue_generation_ui():
    with gr.Blocks() as dialogue_generation_interface:
        gr.Markdown("## Step 3: Dialogue Generation")
        
        # 创建初始DataFrame
        initial_df = create_initial_df(get_language_encoding("中文"))
        
        # 主要的对话表格 - 使用简化版本避免JSON schema问题
        dialogue_df = gr.Textbox(
            value="等待加载台词数据...",
            label="台词生成表格",
            interactive=False,
            lines=20,
            max_lines=30
        )

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    character_dropdown = gr.Dropdown(
                        label="选择角色", 
                        choices=[(c[1], c[0]) for c in db.get_characters()], 
                        interactive=True
                    )
                    llm_config_dropdown = gr.Dropdown(
                        label="LLM配置", 
                        choices=[(c[1], c[0]) for c in db.get_llm_configs()], 
                        interactive=True
                    )
                language_dropdown = gr.Dropdown(
                    label="台词语言", 
                    choices=["中文", "English", "日本語"], 
                    value="中文", 
                    interactive=True
                )
                
                # 数据库管理区域（主要功能）
                with gr.Accordion("💾 对话集管理（数据库）", open=True):
                    with gr.Row():
                        load_dialogue_set_dropdown = gr.Dropdown(
                            label="加载已保存的对话集", 
                            choices=[], 
                            interactive=True
                        )
                        refresh_dialogue_sets_button = gr.Button("🔄 刷新", size="sm")
                    with gr.Row():
                        save_dialogue_set_button = gr.Button("💾 保存至数据库", variant="secondary")
                        delete_dialogue_set_button = gr.Button("🗑️ 删除对话集", variant="stop")

                # CSV导入导出区域（辅助功能）
                with gr.Accordion("📁 CSV导入/导出", open=False):
                    with gr.Row():
                        import_csv_button = gr.File(
                            label="导入CSV文件", 
                            file_types=[".csv"], 
                            type="filepath"
                        )
                        export_csv_button = gr.Button("📤 导出为CSV")

            with gr.Column(scale=2):
                with gr.Row():
                    generate_button = gr.Button("🚀 开始生成台词", variant="primary", size="lg")
                    stop_button = gr.Button("⏹️ 停止生成", variant="stop", interactive=False)
        
        with gr.Row():
            regenerate_selected_button = gr.Button("🔄 重新生成选中台词", variant="secondary", interactive=False)

        # LLM通讯状态和提示词预览窗口
        with gr.Row():
            with gr.Column():
                generation_status = gr.Textbox(
                    label="🔄 LLM通讯状态", 
                    value="等待开始生成...", 
                    interactive=False,
                    lines=15,
                    max_lines=15
                )
            with gr.Column():
                prompt_preview = gr.Textbox(
                    label="📝 当前提示词", 
                    value="请先选择角色、API配置和语言", 
                    interactive=False,
                    lines=15,
                    max_lines=15
                )
        
        status_output = gr.Textbox(label="操作状态", interactive=False)

        # 全局状态
        is_generating = gr.State(False)
        
        def get_characters_and_configs():
            characters = db.get_characters()
            configs = db.get_llm_configs()
            return gr.update(choices=[(c[1], c[0]) for c in characters]), gr.update(choices=[(c[1], c[0]) for c in configs])

        def get_dialogue_sets(character_id):
            if character_id:
                sets = db.get_dialogue_sets(character_id)
                return gr.update(choices=[(s[1], s[0]) for s in sets])
            return gr.update(choices=[])

        def save_dialogue_set(character_id, language, df_data):
            if character_id and df_data:
                try:
                    df = pd.DataFrame(df_data)
                    if df.empty:
                        return "没有台词数据可保存", "没有台词数据可保存"
                    
                    # 生成唯一的集合名称
                    timestamp = time.strftime('%Y%m%d_%H%M%S')
                    character_name = "Unknown"
                    characters = db.get_characters()
                    for char in characters:
                        if char[0] == character_id:
                            character_name = char[1]
                            break
                    
                    set_name = f"{character_name}_{language}_{timestamp}"
                    
                    # 准备对话数据
                    dialogues = []
                    
                    for _, row in df.iterrows():
                        action_param = str(row.get("动作参数", ""))
                        dialogue_text = str(row.get(language, ""))
                        
                        if action_param and dialogue_text and action_param != "nan" and dialogue_text != "nan":
                            dialogues.append((action_param, dialogue_text))
                    
                    if dialogues:
                        # 保存到数据库
                        db.add_dialogue_set(character_id, set_name, dialogues)
                        
                        # 可选：同时导出CSV备份
                        try:
                            output_dir = "output"
                            os.makedirs(output_dir, exist_ok=True)
                            
                            char_output_dir = os.path.join(output_dir, character_name)
                            os.makedirs(char_output_dir, exist_ok=True)
                            
                            backup_path = os.path.join(char_output_dir, f"{set_name}_backup.csv")
                            df.to_csv(backup_path, index=False, encoding='utf-8-sig')
                            
                            success_msg = f"台词集合'{set_name}'已保存到数据库，并备份到: {backup_path}"
                            return success_msg, f"✅ 已保存: {set_name}"
                        except Exception as backup_error:
                            print(f"备份CSV失败: {backup_error}")
                            success_msg = f"台词集合'{set_name}'已保存到数据库"
                            return success_msg, f"✅ 已保存: {set_name}"
                    else:
                        return "没有有效的台词数据可保存", "❌ 没有有效数据"
                        
                except Exception as e:
                    error_msg = f"保存失败: {str(e)}"
                    return error_msg, f"❌ 保存失败"
            return "请选择角色并确保有台词数据", "❌ 缺少必要信息"

        def load_dialogue_set(set_id):
            if set_id:
                try:
                    dialogues = db.get_dialogues(set_id)
                    if dialogues:
                        # 创建DataFrame
                        df_data = []
                        for action_param, dialogue_text in dialogues:
                            row = {"动作参数": action_param, "选择": ""}
                            # 根据对话内容判断语言并填入相应列
                            # 这里简化处理，可以根据实际需要改进
                            if any(ord(char) > 127 for char in dialogue_text):
                                row["中文"] = dialogue_text
                                row["English"] = ""
                                row["日本語"] = ""
                            else:
                                row["中文"] = ""
                                row["English"] = dialogue_text
                                row["日本語"] = ""
                            df_data.append(row)
                        
                        return df_data, f"✅ 已加载对话集: {set_id}"
                    else:
                        return [], f"❌ 对话集为空: {set_id}"
                except Exception as e:
                    return [], f"❌ 加载失败: {str(e)}"
            return [], "❌ 请选择要加载的对话集"

        def delete_dialogue_set(set_id):
            if set_id:
                try:
                    db.delete_dialogue_set(set_id)
                    return f"对话集 {set_id} 已删除", f"✅ 已删除: {set_id}"
                except Exception as e:
                    return f"删除失败: {str(e)}", f"❌ 删除失败"
            return "请选择要删除的对话集", "❌ 请选择对话集"

        def export_to_csv(character_id, language, df_data):
            """导出台词到CSV文件"""
            if not df_data:
                return "没有数据可导出", "❌ 没有数据"
            
            try:
                df = pd.DataFrame(df_data)
                if df.empty:
                    return "没有数据可导出", "❌ 没有数据"
                
                # 获取角色名称
                character_name = "Unknown"
                if character_id:
                    characters = db.get_characters()
                    for char in characters:
                        if char[0] == character_id:
                            character_name = char[1]
                            break
                
                # 创建输出目录
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                
                char_output_dir = os.path.join(output_dir, character_name)
                os.makedirs(char_output_dir, exist_ok=True)
                
                # 生成文件名
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"{character_name}_{language}_{timestamp}.csv"
                filepath = os.path.join(char_output_dir, filename)
                
                # 导出CSV
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                
                return f"已导出到: {filepath}", f"✅ 已导出: {filename}"
                
            except Exception as e:
                return f"导出失败: {str(e)}", f"❌ 导出失败"

        def handle_import_csv(character_id, file_path):
            """处理CSV导入"""
            if not file_path or not character_id:
                return [], "请选择角色和CSV文件", "❌ 缺少必要信息"
            
            try:
                # 读取CSV文件
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                
                # 验证CSV格式
                required_columns = ["动作参数"]
                if not all(col in df.columns for col in required_columns):
                    return [], f"CSV格式错误，需要包含列: {required_columns}", "❌ 格式错误"
                
                # 确保必要的列存在
                for lang in ["中文", "English", "日本語"]:
                    if lang not in df.columns:
                        df[lang] = ""
                
                if "选择" not in df.columns:
                    df["选择"] = ""
                
                # 转换为列表格式
                df_data = df.to_dict('records')
                
                # 生成唯一的集合名称并保存到数据库
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                character_name = "Unknown"
                characters = db.get_characters()
                for char in characters:
                    if char[0] == character_id:
                        character_name = char[1]
                        break
                
                set_name = f"imported_{character_name}_{timestamp}"
                
                # 准备对话数据并保存到数据库
                dialogues = []
                for _, row in df.iterrows():
                    action_param = str(row.get("动作参数", ""))
                    # 尝试从各语言列中找到对话内容
                    dialogue_text = ""
                    for lang in ["中文", "English", "日本語"]:
                        text = str(row.get(lang, ""))
                        if text and text != "nan" and text.strip():
                            dialogue_text = text
                            break
                    
                    if action_param and dialogue_text and action_param != "nan":
                        dialogues.append((action_param, dialogue_text))
                
                if dialogues:
                    db.add_dialogue_set(character_id, set_name, dialogues)
                
                return df_data, f"成功导入 {len(df_data)} 条记录", f"✅ 已导入: {len(df_data)} 条"
                
            except Exception as e:
                return [], f"导入失败: {str(e)}", f"❌ 导入失败"

        def regenerate_selected_dialogue(character_id, llm_config_id, language, df, evt: gr.SelectData):
            if evt.index[1] == 2 or evt.index[1] == 3: # EN or ZH column
                row_index = evt.index[0]
                action_param = df.iloc[row_index, 1]
                
                # Create a temporary single-row DataFrame for generation
                temp_df = pd.DataFrame([df.iloc[row_index]])
                
                # This is a simplified call, you might need to adapt it
                # to use the full streaming logic if you want real-time updates
                # for single-cell regeneration.
                # For now, we continue to the next item
                
                # Get client and prompts
                client, system_prompt, user_prompt_template, generation_params = get_llm_client_and_prompts(llm_config_id)
                if not client:
                    return df, "LLM client not configured."

                user_prompt = user_prompt_template.format(dialogue=action_param)
                
                try:
                    response = client.chat.completions.create(
                        model=db.get_llm_config(llm_config_id)[4],
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        **generation_params
                    )
                    generated_text = response.choices[0].message.content
                    
                    # Update the DataFrame
                    df.iloc[row_index, evt.index[1]] = generated_text
                    
                    return df, f"Regenerated dialogue for '{action_param}'."
                
                except Exception as e:
                    return df, f"Error during regeneration: {e}"

            return df, "" # No change if not a text column

        def update_table_headers(language):
            if language == "EN":
                return gr.update(columns=["选择", "Action Parameter", "EN", "ZH", "Audio"])
            else: # ZH
                return gr.update(columns=["选择", "Action Parameter", "ZH", "EN", "Audio"])

        def get_llm_client_and_prompts(llm_config_id):
            if not llm_config_id:
                return None, None, None, None
            config = db.get_llm_config(llm_config_id)
            if not config:
                return None, None, None, None
            
            from openai import OpenAI
            client = OpenAI(base_url=config[2], api_key=config[3])
            
            system_prompt = config[5]
            user_prompt_template = config[6]
            generation_params = json.loads(config[7]) if config[7] else {}
            
            return client, system_prompt, user_prompt_template, generation_params

        def handle_button_click(character_id, llm_config_id, language, df_data):
            # This function now simply delegates to the streaming function
            # and handles the UI updates before and after.
            
            yield gr.update(interactive=False), gr.update(interactive=True), "Starting generation...", "Preparing...", ""
            
            # Create a generator object from the streaming function
            gen = generate_dialogue_streaming(character_id, llm_config_id, language, df_data)
            
            # Iterate through the generator to get updates
            final_df = None
            final_status = ""
            try:
                for update in gen:
                    # Each update is a tuple (df, status, prompt)
                    df_update, status_update, prompt_update = update
                    final_df = df_update
                    final_status = status_update
                    yield df_update, status_update, "Generating...", prompt_update, gr.update(interactive=False)
            except Exception as e:
                final_status = f"An error occurred: {e}"
            
            # Final update after generation is complete or an error occurred
            yield final_df, final_status, "Finished", "", gr.update(interactive=True)

        def stop_generation():
            # This is a placeholder for the actual stop logic
            # The real implementation will depend on how the generation thread is managed
            print("Stop button clicked. Generation will be stopped if possible.")
            return "Stop signal received. Attempting to stop...", "Stopping...", gr.update(interactive=True)

        def regenerate_selected_dialogues(character_id, llm_config_id, language, df_data):
            if not character_id or not llm_config_id:
                return df_data, "Error: Character and LLM Configuration must be selected."
        
            df = pd.DataFrame(df_data)
            if df.empty:
                return df, "Error: Dialogue table is empty."
        
            # 强制确保数据类型正确，防止nan问题
            if '动作参数' in df.columns:
                df['动作参数'] = df['动作参数'].astype(str).fillna('')
            if '选择' in df.columns:
                df['选择'] = df['选择'].astype(str)
            
            # 确保台词列是字符串类型
            for col in df.columns:
                if col not in ['选择', '动作参数']:
                    df[col] = df[col].astype(str).fillna('')
        
            client, system_prompt, user_prompt_template, generation_params = get_llm_client_and_prompts(llm_config_id)
            if not client:
                return df, "Error: LLM client not configured."
        
            # Find selected rows
            selected_indices = []
            for index, row in df.iterrows():
                if str(row.get("选择", "")).lower() in ["true", "1", "yes"]:
                    selected_indices.append(index)
        
            if not selected_indices:
                return df, "No dialogues selected for regeneration."
        
            # Regenerate selected dialogues
            for index in selected_indices:
                action_param = df.at[index, "动作参数"]
                language_map = {"中文": "Chinese", "English": "English", "日本語": "Japanese"}
                pronoun_map = {"中文": "你", "English": "you", "日本語": "あなた"}
                target_language = language_map.get(language, "Chinese")
                pronoun = pronoun_map.get(language, "你")

                strict_system_prompt = (
                    f"{system_prompt}\n\n"
                    f"IMPORTANT: STRICT LANGUAGE RULES:\n"
                    f"- Write all output exclusively in {target_language}.\n"
                    f"- Do not mix other languages and do not include any translation.\n"
                    f"- Always address the user ONLY with '{pronoun}'. Never use names or nicknames.\n"
                    f"- For Japanese, use kana and kanji only; romaji strictly prohibited."
                )

                base_user_prompt = user_prompt_template.format(dialogue=action_param)
                strict_user_prompt = (
                    f"{base_user_prompt}\n\n"
                    f"STRICT LANGUAGE REQUIREMENT:\n"
                    f"- Output must be solely in {target_language}.\n"
                    f"- No other languages, no translation.\n"
                    f"- If {target_language} == Japanese: use kana/kanji only, no romaji.\n"
                    f"Return one dialogue line only."
                )
        
                try:
                    response = client.chat.completions.create(
                        model=db.get_llm_config(llm_config_id)[4],
                        messages=[
                            {"role": "system", "content": strict_system_prompt},
                            {"role": "user", "content": strict_user_prompt}
                        ],
                        **generation_params
                    )
                    
                    generated_content = response.choices[0].message.content
                    df.at[index, language] = generated_content
        
                except Exception as e:
                    df.at[index, language] = f"ERROR: {e}"
        
            # Auto-save after regeneration
            auto_save_after_generation(character_id, df)
            
            return df, f"Regenerated {len(selected_indices)} selected dialogues."

        def toggle_regenerate_button(df_value):
            try:
                has_selected = False
                if isinstance(df_value, pd.DataFrame):
                    if "选择" in df_value.columns:
                        has_selected = bool(df_value["选择"].astype(bool).any())
                else:
                    # Handle non-DataFrame structures (like lists)
                    temp_df = pd.DataFrame(df_value) if df_value is not None else pd.DataFrame()
                    if not temp_df.empty:
                        # Assume the first column is the selection column
                        has_selected = bool(temp_df.iloc[:, 0].astype(bool).any())
                return gr.update(interactive=has_selected)
            except Exception:
                return gr.update(interactive=False)

        def refresh_csv_files(character_id):
            """Refresh the list of CSV files for the character."""
            if not character_id:
                return gr.update(choices=[])
            
            character = db.get_character(character_id)
            if not character:
                return gr.update(choices=[])
            
            csv_files = get_character_csv_files(character[1])
            return gr.update(choices=csv_files)
        
        def handle_load_csv(character_id, csv_filename):
            """Handle loading a CSV file."""
            if not character_id or not csv_filename:
                return "Please select a character and a CSV file.", initial_df.copy()
            
            character = db.get_character(character_id)
            if not character:
                return "Character not found.", initial_df.copy()
            
            loaded_df = load_csv_file(character[1], csv_filename)
            return f"Successfully loaded file: {csv_filename}", loaded_df
        
        def handle_save_csv(character_id, custom_filename, dialogue_df_data):
            """Handle saving a CSV file."""
            if not character_id:
                return "Please select a character first."
            
            character = db.get_character(character_id)
            if not character:
                return "Character not found."
            
            result = save_current_dialogue(character[1], dialogue_df_data, custom_filename)
            return result
        
        def handle_import_csv(character_id, csv_file):
            """Handle importing a CSV file."""
            if not character_id:
                return "Please select a character first.", initial_df.copy(), "Please select a character first."
            
            character = db.get_character(character_id)
            if not character:
                return "Character not found.", initial_df.copy(), "Character not found."
            
            status, df = import_external_csv(character[1], csv_file)
            return df, status, status
        
        def auto_save_after_generation(character_id, dialogue_df_data):
            """Auto-save after generation is complete."""
            if not character_id or dialogue_df_data is None:
                return
            
            character = db.get_character(character_id)
            if character:
                filename = auto_save_dialogue_csv(character[1], dialogue_df_data)
                if filename:
                    print(f"Generation complete, auto-saved as: {filename}")

        # 事件绑定
        # language_dropdown.change(update_table_headers, language_dropdown, dialogue_df)
        character_dropdown.change(get_dialogue_sets, character_dropdown, load_dialogue_set_dropdown)

        # character_dropdown.change(refresh_csv_files, character_dropdown, csv_files_dropdown)
        # refresh_csv_button.click(refresh_csv_files, character_dropdown, csv_files_dropdown)
        # load_csv_button.click(handle_load_csv, [character_dropdown, csv_files_dropdown], [csv_status, dialogue_df])
        # save_csv_button.click(handle_save_csv, [character_dropdown, save_filename_input, dialogue_df], csv_status).then(
        #     refresh_csv_files, character_dropdown, csv_files_dropdown
        # )

        # refresh_llm_button.click(refresh_llm_configs, None, llm_config_dropdown)

        def update_prompt_preview(character_id, llm_config_id, language):
            return preview_prompt(character_id, llm_config_id, language)

        # 生成台词事件
        gen_evt = generate_button.click(
            generate_dialogue_streaming,
            [character_dropdown, llm_config_dropdown, language_dropdown, dialogue_df],
            [dialogue_df, generation_status, prompt_preview],
            show_progress=True
        )

        # 停止生成事件
        stop_button.click(
            lambda: (gr.update(interactive=True), "Generation stopped.", ""),
            outputs=[generate_button, generation_status, prompt_preview]
        )

        # 重新生成选中台词事件
        regenerate_selected_button.click(
            regenerate_selected_dialogues,
            [character_dropdown, llm_config_dropdown, language_dropdown, dialogue_df],
            [dialogue_df, generation_status, prompt_preview]
        )

        # 切换重新生成按钮状态
        dialogue_df.change(toggle_regenerate_button, dialogue_df, regenerate_selected_button)

        # 数据库管理事件
        save_dialogue_set_button.click(
            save_dialogue_set,
            [character_dropdown, language_dropdown, dialogue_df],
            [status_output, generation_status]
        ).then(
            get_dialogue_sets,
            character_dropdown,
            load_dialogue_set_dropdown
        )

        load_dialogue_set_dropdown.change(
            load_dialogue_set,
            load_dialogue_set_dropdown,
            [dialogue_df, generation_status]
        ).then(
            toggle_regenerate_button,
            dialogue_df,
            regenerate_selected_button
        )

        delete_dialogue_set_button.click(
            delete_dialogue_set,
            load_dialogue_set_dropdown,
            [status_output, generation_status]
        ).then(
            get_dialogue_sets,
            character_dropdown,
            load_dialogue_set_dropdown
        )

        refresh_dialogue_sets_button.click(
            get_dialogue_sets,
            character_dropdown,
            load_dialogue_set_dropdown
        )

        # CSV导入导出事件
        import_csv_button.change(
            handle_import_csv,
            [character_dropdown, import_csv_button],
            [dialogue_df, status_output, generation_status]
        )

        export_csv_button.click(
            export_to_csv,
            [character_dropdown, language_dropdown, dialogue_df],
            [status_output, generation_status]
        )

        # 提示词预览更新事件
        character_dropdown.change(
            update_prompt_preview,
            [character_dropdown, llm_config_dropdown, language_dropdown],
            prompt_preview
        )

        llm_config_dropdown.change(
            update_prompt_preview,
            [character_dropdown, llm_config_dropdown, language_dropdown],
            prompt_preview
        )

        language_dropdown.change(
            update_prompt_preview,
            [character_dropdown, llm_config_dropdown, language_dropdown],
            prompt_preview
        )

        dialogue_generation_interface.load(get_characters_and_configs, None, [character_dropdown, llm_config_dropdown])

    return dialogue_generation_interface

def refresh_llm_configs():
    configs = db.get_llm_configs()
    return gr.update(choices=[(c[1], c[0]) for c in configs])

def generate_dialogue_streaming(character_id, llm_config_id, language, df_data):
    if not character_id or not llm_config_id:
        yield df_data, "Error: Character and LLM Configuration must be selected.", ""
        return

    df = pd.DataFrame(df_data)
    if df.empty:
        yield df, "Error: Dialogue table is empty.", ""
        return

    # 强制确保数据类型正确，防止nan问题
    if '动作参数' in df.columns:
        df['动作参数'] = df['动作参数'].astype(str).fillna('')
    if '选择' in df.columns:
        df['选择'] = df['选择'].astype(str)
    
    # 确保台词列是字符串类型
    for col in df.columns:
        if col not in ['选择', '动作参数']:
            df[col] = df[col].astype(str).fillna('')

    client, system_prompt, user_prompt_template, generation_params = get_llm_client_and_prompts(llm_config_id)
    if not client:
        yield df, "Error: LLM client not configured.", ""
        return

    # Main generation loop
    for index, row in df.iterrows():
        action_param = row["动作参数"]
        
        # Skip if dialogue already exists for the target language
        if pd.notna(row[language]) and row[language].strip():
            continue

        # Strict language compliance mapping and rules
        language_map = {"中文": "Chinese", "English": "English", "日本語": "Japanese"}
        pronoun_map = {"中文": "你", "English": "you", "日本語": "あなた"}
        target_language = language_map.get(language, "Chinese")
        pronoun = pronoun_map.get(language, "你")

        strict_system_prompt = (
            f"{system_prompt}\n\n"
            f"IMPORTANT: STRICT LANGUAGE RULES:\n"
            f"- Write all output exclusively in {target_language}.\n"
            f"- Do not mix other languages and do not include any translation.\n"
            f"- Always address the user ONLY with '{pronoun}'. Never use names or nicknames.\n"
            f"- For Japanese, use kana and kanji only; romaji strictly prohibited."
        )

        base_user_prompt = user_prompt_template.format(dialogue=action_param)
        strict_user_prompt = (
            f"{base_user_prompt}\n\n"
            f"STRICT LANGUAGE REQUIREMENT:\n"
            f"- Output must be solely in {target_language}.\n"
            f"- No other languages, no translation.\n"
            f"- If {target_language} == Japanese: use kana/kanji only, no romaji.\n"
            f"Return one dialogue line only."
        )
        
        # Update prompt preview
        full_prompt_for_preview = f"System: {strict_system_prompt}\n\nUser: {strict_user_prompt}"
        yield df, f"Generating for: {action_param}", full_prompt_for_preview

        try:
            stream = client.chat.completions.create(
                model=db.get_llm_config(llm_config_id)[4],
                messages=[
                    {"role": "system", "content": strict_system_prompt},
                    {"role": "user", "content": strict_user_prompt}
                ],
                stream=True,
                **generation_params
            )
            
            # Stream handling
            collected_chunks = []
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                collected_chunks.append(content)
                
                # Update DataFrame with partial result
                df.at[index, language] = "".join(collected_chunks)
                yield df, f"Streaming for: {action_param}", full_prompt_for_preview

        except Exception as e:
            error_message = f"Error generating for '{action_param}': {e}"
            df.at[index, language] = f"ERROR: {e}"
            yield df, error_message, full_prompt_for_preview
            # Decide whether to continue or stop on error
            # For now, we continue to the next item
    
    # Final yield after loop completion
    yield df, "All dialogues generated.", ""
    
    # Auto-save after successful generation
    auto_save_after_generation(character_id, df)

def preview_prompt(character_id, llm_config_id, language):
    if not character_id or not llm_config_id:
        return "Select character and LLM config to see the prompt."

    _, system_prompt, user_prompt_template, _ = get_llm_client_and_prompts(llm_config_id)
    
    # For preview, we'll just show the template
    return f"System Prompt:\n{system_prompt}\n\nUser Prompt Template:\n{user_prompt_template}"

def update_character_info(character_input):
    """更新角色信息显示 - 支持角色ID或角色名称"""
    if not character_input:
        return gr.update(value=None), gr.update(value="请选择角色")
    
    try:
        # 判断输入是角色ID还是角色名称
        character = None
        character_name = None
        
        # 先尝试作为角色ID查询
        try:
            if isinstance(character_input, (int, str)) and str(character_input).isdigit():
                character = db.get_character(int(character_input))
                if character:
                    character_name = character[1]
        except:
            pass
        
        # 如果没有找到，尝试作为角色名称查询
        if not character:
            characters = db.get_characters()
            for c in characters:
                if c[1] == character_input:  # c[1] 是角色名称
                    character = c
                    character_name = c[1]
                    break
        
        if not character:
            return gr.update(value=None), gr.update(value="角色不存在")
        
        # 获取角色头像路径 - 复用第三步的逻辑
        image_path = file_manager.get_character_original_avatar_path(character_name)
        
        # 检查图片文件是否存在
        if isinstance(image_path, str) and os.path.exists(image_path):
            image_value = image_path
        else:
            image_value = None
        
        # 获取角色描述 - 复用第三步的逻辑
        # 优先从文件系统获取描述
        desc_text = file_manager.get_character_description(character_name)
        if not isinstance(desc_text, str) or not desc_text.strip():
            # 如果文件系统中没有，则使用数据库中的描述
            desc_text = character[2] if len(character) > 2 and character[2] else ""
        
        # 如果仍然没有描述，提供默认文本
        if not desc_text.strip():
            desc_text = f"角色：{character_name}\n暂无详细描述"
        
        # 替换占位符 - 与第三步保持一致
        desc_text = desc_text.replace("{{char}}", character_name).replace("{{user}}", "用户")
        
        return gr.update(value=image_value), gr.update(value=desc_text)
        
    except Exception as e:
        print(f"更新角色信息失败: {e}")
        import traceback
        traceback.print_exc()
        return gr.update(value=None), gr.update(value=f"加载角色信息失败: {str(e)}")

def voice_generation_ui():
    with gr.Blocks() as voice_generation_ui:
        gr.Markdown("## 第四步：语音生成")
        
        # 选择区域
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    character_dropdown = gr.Dropdown(label="选择角色", interactive=True, scale=4)
                    refresh_character_btn = gr.Button("🔄", size="sm", variant="secondary", min_width=40, scale=0)
            with gr.Column():
                with gr.Row():
                    dialogue_set_dropdown = gr.Dropdown(label="选择台词集", interactive=True, scale=4)
                    refresh_dialogue_set_btn = gr.Button("🔄", size="sm", variant="secondary", min_width=40, scale=0)
            with gr.Column():
                with gr.Row():
                    voice_id_dropdown = gr.Dropdown(label="选择语音ID", interactive=True, scale=4)
                    refresh_voice_ids_btn = gr.Button("🔄", size="sm", variant="secondary", min_width=40, scale=0)
        
        # 角色信息展示区域
        with gr.Row():
            character_image = gr.Image(label="", interactive=False, width=300, height=400)
            character_description = gr.Textbox(label="", interactive=False, lines=18, max_lines=18)
        
        # 台词集展示区域
        gr.Markdown("### 台词集")
        
        # 操作按钮区域
        with gr.Row():
            select_all_btn = gr.Button("全选", size="sm")
            select_none_btn = gr.Button("全不选", size="sm")
            generate_selected_btn = gr.Button("🎯 生成选中的语音", variant="primary")
            stop_generation_btn = gr.Button("⏹️ 停止生成", variant="stop", visible=False)
            save_package_btn = gr.Button("💾 保存音频文件包", variant="secondary")
        
        # 状态显示
        status_text = gr.Textbox(label="操作状态", interactive=False, max_lines=3)
        
        # 存储当前台词数据
        current_dialogue_data = gr.State([])
        
        # 表头
        with gr.Row():
            gr.HTML("<div style='width: 32px; text-align: center; font-weight: bold;'>选择</div>")
            gr.HTML("<div style='flex: 3; text-align: center; font-weight: bold;'>动作参数</div>")
            gr.HTML("<div style='flex: 6; text-align: center; font-weight: bold;'>台词</div>")
            gr.HTML("<div style='flex: 3; text-align: center; font-weight: bold;'>音频</div>")
        
        # 预创建固定数量的UI组件（类似台词生成界面）
        MAX_ROWS = 200
        dialogue_checkboxes = []
        action_param_textboxes = []
        dialogue_textboxes = []
        audio_outputs = []
        
        # 创建固定数量的行
        for i in range(MAX_ROWS):
            with gr.Row(visible=True) as row:  # 改为默认可见
                checkbox = gr.Checkbox(
                    label="", 
                    value=True, 
                    scale=0, 
                    min_width=32, 
                    show_label=False
                )
                action_param = gr.Textbox(
                    label="", 
                    value="", 
                    interactive=False, 
                    scale=3, 
                    show_label=False
                )
                text = gr.Textbox(
                    label="", 
                    value="", 
                    interactive=False, 
                    scale=6, 
                    show_label=False
                )
                # 简化的音频播放器，移动到状态栏原来的位置
                audio = gr.Audio(
                    label="", 
                    value=None, 
                    interactive=False, 
                    scale=3, 
                    show_label=False,
                    show_download_button=False,
                    show_share_button=False
                )
                
                dialogue_checkboxes.append(checkbox)
                action_param_textboxes.append(action_param)
                dialogue_textboxes.append(text)
                audio_outputs.append(audio)

        def get_characters_and_voice_ids():
            """获取角色列表和语音ID列表"""
            try:
                characters = db.get_characters()
                character_choices = [(c[1], c[1]) for c in characters]  # 使用角色名称作为值，而不是ID
            except Exception as e:
                print(f"数据库连接失败，使用文件系统获取角色列表: {e}")
                # 如果数据库连接失败，直接从文件系统获取角色列表
                characters_dir = "/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Characters"
                if os.path.exists(characters_dir):
                    character_folders = [d for d in os.listdir(characters_dir) 
                                       if os.path.isdir(os.path.join(characters_dir, d))]
                    character_choices = [(name, name) for name in character_folders]
                else:
                    character_choices = []
            
            # 自动刷新语音ID列表
            voice_id_choices = refresh_voice_ids()
            # 按字母顺序排序
            voice_id_choices = sorted(voice_id_choices, key=lambda x: x[0].lower())
            
            if character_choices:
                # 使用新的台词集获取方法
                character_name = character_choices[0][1]
                dialogue_set_choices = get_dialogue_sets_from_files(character_name)
                
                # 设置默认选择第一项语音ID
                voice_id_default = voice_id_choices[0][1] if voice_id_choices else None
                
                return (
                    gr.update(choices=character_choices, value=character_choices[0][1]),
                    gr.update(choices=dialogue_set_choices),
                    gr.update(choices=voice_id_choices, value=voice_id_default)
                )
            else:
                # 即使没有角色，也要设置语音ID的默认选择
                voice_id_default = voice_id_choices[0][1] if voice_id_choices else None
                return (
                    gr.update(choices=[]),
                    gr.update(choices=[]),
                    gr.update(choices=voice_id_choices, value=voice_id_default)
                )

        def refresh_voice_ids():
            """从API刷新语音ID列表"""
            try:
                import requests
                response = requests.get("https://tts.ioioioioio.com:1120/breathvoice/voice-groups", timeout=5, verify=False)
                if response.status_code == 200:
                    data = response.json()
                    voice_ids = data.get('voice_groups', [])
                    voice_id_choices = [(vid, vid) for vid in voice_ids]
                    return voice_id_choices
                else:
                    # 如果API返回错误，使用默认选项
                    return [("ChineseWoman", "ChineseWoman"), ("EnglishGirl", "EnglishGirl")]
            except:
                # 如果API不可用，使用默认选项
                return [("ChineseWoman", "ChineseWoman"), ("EnglishGirl", "EnglishGirl")]

        def refresh_voice_ids_button_click():
            """刷新按钮点击事件"""
            voice_id_choices = refresh_voice_ids()
            # 按字母顺序排序
            voice_id_choices = sorted(voice_id_choices, key=lambda x: x[0].lower())
            # 设置默认选择第一项
            voice_id_default = voice_id_choices[0][1] if voice_id_choices else None
            return gr.update(choices=voice_id_choices, value=voice_id_default)

        def get_dialogue_sets_from_files(character_name):
            """从角色文件夹的script目录获取台词集"""
            if not character_name:
                return []
            
            script_dir = f"/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Characters/{character_name}/script"
            
            if not os.path.exists(script_dir):
                return [("该角色没有可用的台词集", "")]
            
            csv_files = [f for f in os.listdir(script_dir) if f.endswith('.csv')]
            
            if not csv_files:
                return [("该角色没有可用的台词集", "")]
            
            dialogue_set_choices = []
            for csv_file in csv_files:
                display_name = os.path.splitext(csv_file)[0]  # 去掉.csv扩展名
                full_path = os.path.join(script_dir, csv_file)
                dialogue_set_choices.append((display_name, full_path))
            
            return dialogue_set_choices

        def update_dialogue_sets(character_name):
            """更新台词集选项"""
            dialogue_set_choices = get_dialogue_sets_from_files(character_name)
            return gr.update(choices=dialogue_set_choices)

        def update_dialogue_display_with_ui(csv_file_path):
            """根据CSV文件内容更新预创建的UI组件"""
            if not csv_file_path or not os.path.exists(csv_file_path):
                # 隐藏所有行
                updates = []
                for i in range(MAX_ROWS):
                    updates.extend([
                        gr.update(value=True),     # Checkbox
                        gr.update(value=""),       # Action param
                        gr.update(value=""),       # Dialogue
                        gr.update(value=None)      # Audio
                    ])
                updates.append([])  # Current dialogue data
                updates.append("没有选择有效的台词集文件")  # Status text
                return updates
            
            try:
                # 读取CSV文件
                df = pd.read_csv(csv_file_path)
                dialogue_data = []
                
                # 处理数据
                for index, row in df.iterrows():
                    action_param = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                    dialogue = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
                    
                    if action_param.strip() and dialogue.strip():  # 过滤空行
                        dialogue_data.append({
                            'action_param': action_param,
                            'dialogue': dialogue,
                            'audio_path': None,
                            'selected': True
                        })
                
                # 更新UI组件
                updates = []
                for i in range(MAX_ROWS):
                    if i < len(dialogue_data):
                        data = dialogue_data[i]
                        updates.extend([
                            gr.update(value=True),                      # Checkbox
                            gr.update(value=data['action_param']),      # Action param
                            gr.update(value=data['dialogue']),          # Dialogue
                            gr.update(value=None)                       # Audio
                        ])
                    else:
                        updates.extend([
                            gr.update(value=True),     # Checkbox
                            gr.update(value=""),       # Action param
                            gr.update(value=""),       # Dialogue
                            gr.update(value=None)      # Audio
                        ])
                
                updates.append(dialogue_data)  # Current dialogue data
                updates.append(f"成功加载 {len(dialogue_data)} 条台词")  # Status text
                return updates
                
            except Exception as e:
                # 隐藏所有行
                updates = []
                for i in range(MAX_ROWS):
                    updates.extend([
                        gr.update(value=True),     # Checkbox
                        gr.update(value=""),       # Action param
                        gr.update(value=""),       # Dialogue
                        gr.update(value=None)      # Audio
                    ])
                updates.append([])  # Current dialogue data
                updates.append(f"加载台词集失败: {str(e)}")  # Status text
                return updates

        # 删除render_dialogue_components函数，因为我们现在使用预创建的组件

        def select_all_dialogues(current_data):
            """全选所有台词"""
            if current_data is None or len(current_data) == 0:
                return [gr.update(value=True) for _ in range(MAX_ROWS)] + [gr.update(value="没有可选择的台词")]
            
            # 返回所有复选框的更新，选中状态为True
            updates = []
            for i in range(MAX_ROWS):
                if i < len(current_data):
                    updates.append(gr.update(value=True))
                else:
                    updates.append(gr.update(value=True))
            
            updates.append(gr.update(value=f"已全选 {len(current_data)} 条台词"))
            return updates

        def select_none_dialogues(current_data):
            """取消选择所有台词"""
            if current_data is None or len(current_data) == 0:
                return [gr.update(value=False) for _ in range(MAX_ROWS)] + [gr.update(value="没有可取消选择的台词")]
            
            # 返回所有复选框的更新，选中状态为False
            updates = []
            for i in range(MAX_ROWS):
                if i < len(current_data):
                    updates.append(gr.update(value=False))
                else:
                    updates.append(gr.update(value=False))
            
            updates.append(gr.update(value="已取消选择所有台词"))
            return updates

        # 全局变量用于控制生成过程
        generation_stop_flag = gr.State(False)
        
        def call_single_tts_api(text, filename, voice_group_id, character_name):
            """调用单条TTS生成接口"""
            import requests
            import base64
            import os
            
            try:
                # 准备单条TTS请求数据
                payload = {
                    "text": text,
                    "filename": filename,
                    "voice_group_id": voice_group_id
                }
                
                # 发送单条TTS请求
                response = requests.post(
                    "https://tts.ioioioioio.com:1120/breathvoice/single-tts",
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=60,  # 单条请求超时时间
                    verify=False  # 忽略SSL证书验证
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success", False):
                        # 获取base64编码的音频数据
                        audio_data = result.get("audio_data", "")
                        if audio_data:
                            # 解码base64音频数据
                            audio_bytes = base64.b64decode(audio_data)
                            
                            # 创建角色语音临时文件夹路径
                            character_voices_dir = f"/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Characters/{character_name}/{character_name}_Voices"
                            temp_dir = os.path.join(character_voices_dir, "temp")
                            os.makedirs(temp_dir, exist_ok=True)
                            
                            # 创建临时音频文件
                            audio_file_path = os.path.join(temp_dir, f"{filename}.wav")
                            with open(audio_file_path, 'wb') as f:
                                f.write(audio_bytes)
                            
                            return {
                                "success": True,
                                "audio_path": audio_file_path,
                                "message": "生成成功"
                            }
                        else:
                            return {
                                "success": False,
                                "message": "API返回的音频数据为空"
                            }
                    else:
                        error_msg = result.get("error", "未知错误")
                        return {
                            "success": False,
                            "message": f"API错误: {error_msg}"
                        }
                else:
                    return {
                        "success": False,
                        "message": f"HTTP错误: {response.status_code}"
                    }
                    
            except requests.exceptions.Timeout:
                return {
                    "success": False,
                    "message": "请求超时"
                }
            except requests.exceptions.RequestException as e:
                return {
                    "success": False,
                    "message": f"网络错误: {str(e)}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"生成失败: {str(e)}"
                }

        def stop_generation():
            """停止当前的语音生成过程"""
            generation_stop_flag.value = True
            return (
                gr.update(visible=False),  # 隐藏停止按钮
                gr.update(visible=True),   # 显示生成按钮
                gr.update(value="用户已停止生成过程")  # 更新状态文本
            )

        def generate_selected_voices_sequential(character_name, voice_id, current_data, *checkbox_values):
            """逐条生成选中的语音（支持停止控制和即时音频更新）"""
            # 重置停止标志并显示停止按钮
            generation_stop_flag.value = False
            
            # 准备初始的音频组件更新列表（所有音频组件保持当前状态）
            initial_audio_updates = [gr.update() for _ in range(MAX_ROWS)]
            
            # 首先返回按钮状态更新
            yield (
                gr.update(visible=False),  # 隐藏生成按钮
                gr.update(visible=True),   # 显示停止按钮
                gr.update(value="开始逐条生成...")  # 更新状态文本
            ) + tuple(initial_audio_updates)
            
            if not voice_id:
                yield (
                    gr.update(visible=True),   # 显示生成按钮
                    gr.update(visible=False),  # 隐藏停止按钮
                    gr.update(value="请先选择语音ID")
                ) + tuple(initial_audio_updates)
                return
            
            if current_data is None or len(current_data) == 0:
                yield (
                    gr.update(visible=True),   # 显示生成按钮
                    gr.update(visible=False),  # 隐藏停止按钮
                    gr.update(value="没有可生成的台词数据")
                ) + tuple(initial_audio_updates)
                return
            
            # 获取选中的条目
            selected_items = []
            for i, is_selected in enumerate(checkbox_values[:len(current_data)]):
                if is_selected and i < len(current_data):
                    selected_items.append({
                        'index': i,
                        'action_param': current_data[i]['action_param'],
                        'dialogue_text': current_data[i]['dialogue']
                    })
            
            if not selected_items:
                yield (
                    gr.update(visible=True),   # 显示生成按钮
                    gr.update(visible=False),  # 隐藏停止按钮
                    gr.update(value="请先选择要生成的台词")
                ) + tuple(initial_audio_updates)
                return
            
            # 开始逐条生成
            success_count = 0
            total_count = len(selected_items)
            
            for idx, item in enumerate(selected_items):
                # 检查停止标志
                if generation_stop_flag.value:
                    audio_updates = [gr.update() for _ in range(MAX_ROWS)]
                    yield (
                        gr.update(visible=True),   # 显示生成按钮
                        gr.update(visible=False),  # 隐藏停止按钮
                        gr.update(value=f"用户停止生成 - 已完成 {success_count}/{total_count} 个音频文件")
                    ) + tuple(audio_updates)
                    return
                
                # 更新当前进度
                current_progress = f"正在生成 ({idx + 1}/{total_count}): {item['action_param']} - {item['dialogue_text'][:30]}..."
                audio_updates = [gr.update() for _ in range(MAX_ROWS)]
                yield (
                    gr.update(visible=False),  # 保持生成按钮隐藏
                    gr.update(visible=True),   # 保持停止按钮显示
                    gr.update(value=current_progress)
                ) + tuple(audio_updates)
                
                # 调用单条TTS API
                result = call_single_tts_api(
                    text=item['dialogue_text'],
                    filename=f"{item['action_param']}.wav",
                    voice_group_id=voice_id,
                    character_name=character_name
                )
                
                # 准备音频组件更新列表
                audio_updates = [gr.update() for _ in range(MAX_ROWS)]
                
                if result["success"]:
                    success_count += 1
                    # 更新对应行的状态和音频
                    index = item['index']
                    current_data[index]['audio_path'] = result["audio_path"]
                    status_msg = f"✅ 生成成功 ({idx + 1}/{total_count})"
                    
                    # 更新对应的音频组件
                    if index < MAX_ROWS:
                        audio_updates[index] = gr.update(value=result["audio_path"])
                else:
                    # 生成失败，记录错误信息
                    index = item['index']
                    current_data[index]['audio_path'] = None
                    status_msg = f"❌ 生成失败: {result['message']} ({idx + 1}/{total_count})"
                
                # 更新进度状态和音频组件
                progress_msg = f"进度: {idx + 1}/{total_count} | 成功: {success_count} | {status_msg}"
                yield (
                    gr.update(visible=False),  # 保持生成按钮隐藏
                    gr.update(visible=True),   # 保持停止按钮显示
                    gr.update(value=progress_msg)
                ) + tuple(audio_updates)
                
                # 短暂延迟，让UI有时间更新
                time.sleep(0.1)
            
            # 生成完成，恢复按钮状态
            final_msg = f"🎉 逐条生成完成！成功生成 {success_count}/{total_count} 个音频文件"
            final_audio_updates = [gr.update() for _ in range(MAX_ROWS)]
            yield (
                gr.update(visible=True),   # 显示生成按钮
                gr.update(visible=False),  # 隐藏停止按钮
                gr.update(value=final_msg)
            ) + tuple(final_audio_updates)

        def save_audio_package(character_name, current_data):
            """保存音频文件包，按关键词分类移动文件"""
            if not character_name:
                return gr.update(value="请先选择角色")
            
            if current_data is None or len(current_data) == 0:
                return gr.update(value="没有可保存的音频文件")
            
            # 获取temp文件夹路径
            character_voices_dir = f"/Users/Saga/Documents/L&B Conceptions/Demo/breathVOICE/Characters/{character_name}/{character_name}_Voices"
            temp_dir = os.path.join(character_voices_dir, "temp")
            
            if not os.path.exists(temp_dir):
                return gr.update(value="临时文件夹不存在")
            
            # 定义关键词到文件夹的映射
            keyword_mapping = {
                "greeting": "greeting",
                "impact": "impact", 
                "reaction": "reaction",
                "tease": "tease",
                "long": "touch",
                "short": "touch",
                "orgasm": "orgasm"
            }
            
            saved_count = 0
            moved_files = {}  # 记录移动的文件：原路径 -> 新路径
            import shutil
            
            # 遍历temp文件夹中的所有文件
            for filename in os.listdir(temp_dir):
                if filename.endswith('.wav'):
                    source_path = os.path.join(temp_dir, filename)
                    
                    # 检查文件名中包含的关键词
                    for keyword, folder_name in keyword_mapping.items():
                        if keyword in filename.lower():
                            # 创建目标文件夹
                            target_folder = os.path.join(character_voices_dir, folder_name)
                            os.makedirs(target_folder, exist_ok=True)
                            
                            # 移动文件到目标文件夹
                            target_path = os.path.join(target_folder, filename)
                            try:
                                shutil.move(source_path, target_path)
                                moved_files[source_path] = target_path
                                saved_count += 1
                                break  # 找到匹配的关键词后跳出循环
                            except Exception as e:
                                print(f"移动文件失败 {filename}: {e}")
            
            # 更新界面中的音频播放器路径
            updated_outputs = []
            for i in range(len(audio_outputs)):
                # 检查当前行是否有对应的数据
                if current_data and i < len(current_data):
                    row_data = current_data[i]
                    if isinstance(row_data, dict) and 'audio_path' in row_data:
                        current_audio_path = row_data['audio_path']
                        if current_audio_path and current_audio_path in moved_files:
                            # 更新音频播放器指向新位置
                            updated_outputs.append(gr.update(value=moved_files[current_audio_path]))
                        else:
                            updated_outputs.append(gr.update())
                    else:
                        updated_outputs.append(gr.update())
                else:
                    updated_outputs.append(gr.update())
            
            return [gr.update(value=f"已按类型分类移动 {saved_count} 个音频文件")] + updated_outputs

        # 事件绑定
        save_package_btn.click(
            save_audio_package,
            [character_dropdown, current_dialogue_data],
            [status_text] + audio_outputs
        )
        character_dropdown.change(update_dialogue_sets, character_dropdown, dialogue_set_dropdown)
        
        # 台词集下拉框变化时更新界面
        # 创建所有输出列表：行可见性 + 每行的4个组件
        all_outputs = []
        for i in range(MAX_ROWS):
            # 每行包含：复选框、动作参数、台词、音频
            all_outputs.extend([
                dialogue_checkboxes[i],
                action_param_textboxes[i],
                dialogue_textboxes[i],
                audio_outputs[i]
            ])
        all_outputs.extend([current_dialogue_data, status_text])
        
        dialogue_set_dropdown.change(
            update_dialogue_display_with_ui, 
            dialogue_set_dropdown, 
            all_outputs
        )
        
        # 全选/全不选按钮
        select_all_btn.click(
            select_all_dialogues, 
            current_dialogue_data, 
            dialogue_checkboxes + [status_text]
        )
        select_none_btn.click(
            select_none_dialogues, 
            current_dialogue_data, 
            dialogue_checkboxes + [status_text]
        )
        
        # 生成语音按钮
        generate_selected_btn.click(
            generate_selected_voices_sequential, 
            [character_dropdown, voice_id_dropdown, current_dialogue_data] + dialogue_checkboxes,
            [generate_selected_btn, stop_generation_btn, status_text] + audio_outputs  # 返回按钮状态、状态文本和所有音频组件
        )
        
        # 停止生成按钮
        stop_generation_btn.click(
            stop_generation,
            outputs=[stop_generation_btn, generate_selected_btn, status_text]
        )
        
        # 页面加载时初始化
        voice_generation_ui.load(get_characters_and_voice_ids, None, [character_dropdown, dialogue_set_dropdown, voice_id_dropdown])
        
        # 刷新按钮事件
        refresh_character_btn.click(
            lambda: gr.update(choices=[(c[1], c[0]) for c in db.get_characters()]),
            outputs=character_dropdown
        )
        
        refresh_dialogue_set_btn.click(
            lambda character_id: gr.update(choices=get_dialogue_sets(character_id) if character_id else []),
            inputs=character_dropdown,
            outputs=dialogue_set_dropdown
        )
        
        refresh_voice_ids_btn.click(refresh_voice_ids_button_click, None, voice_id_dropdown)
        
        # 角色选择变化时更新角色信息
        character_dropdown.change(
            lambda character_id: update_character_info(character_id),
            inputs=character_dropdown,
            outputs=[character_image, character_description]
        )

    return voice_generation_ui

def export_ui():
    with gr.Blocks() as export_interface:
        gr.Markdown("## 第五步：导出语音包")
        
        with gr.Row():
            character_dropdown = gr.Dropdown(label="选择角色", scale=2)
            export_button = gr.Button("🎯 导出语音包", variant="primary", scale=1, interactive=False)
        
        # 进度显示区域
        with gr.Column():
            progress_bar = gr.Progress()
            status_text = gr.Textbox(
                label="导出状态", 
                value="请选择角色", 
                interactive=False,
                lines=3
            )
        
        # 下载区域
        download_file = gr.File(
            label="下载语音包", 
            visible=False,
            interactive=False
        )
        
        # 初始化语音包导出器
        voice_exporter = VoicePackExporter()

        def get_characters():
            """获取角色列表"""
            characters = db.get_characters()
            return gr.update(choices=[(c[1], c[0]) for c in characters])

        def check_voice_files_exist(character_id):
            """检查角色是否有可导出的语音文件"""
            if not character_id:
                return False, "请选择角色"
            
            try:
                character = db.get_character(character_id)
                if not character:
                    return False, "角色不存在"
                
                character_name = character[1]
                source_voices_dir = file_manager.get_voice_directory(character_name)
                
                if not os.path.exists(source_voices_dir):
                    return False, f"语音目录不存在: {source_voices_dir}"
                
                # 检查指定的子文件夹中是否有wav文件
                target_folders = ['greeting', 'orgasm', 'reaction', 'tease', 'impact', 'touch']
                has_wav_files = False
                
                for folder in target_folders:
                    folder_path = os.path.join(source_voices_dir, folder)
                    if os.path.exists(folder_path) and folder != 'temp':
                        # 检查文件夹中是否有.wav文件
                        for file in os.listdir(folder_path):
                            if file.lower().endswith('.wav'):
                                has_wav_files = True
                                break
                        if has_wav_files:
                            break
                
                if not has_wav_files:
                    return False, "该角色尚不存在可导出的语音。"
                
                return True, "角色已选择，可以导出语音包"
                
            except Exception as e:
                return False, f"检查语音文件时出错: {str(e)}"

        def update_export_button_state(character_id):
            """更新导出按钮状态"""
            has_files, message = check_voice_files_exist(character_id)
            return (
                gr.update(interactive=has_files),
                gr.update(value=message)
            )

        def export_voice_pack_with_progress(character_id, progress=gr.Progress()):
            """带进度显示的语音包导出功能"""
            if not character_id:
                return (
                    gr.update(value="❌ 请先选择一个角色", visible=True),
                    gr.update(visible=False)
                )

            try:
                # 获取角色信息
                character = db.get_character(character_id)
                if not character:
                    return (
                        gr.update(value="❌ 角色不存在", visible=True),
                        gr.update(visible=False)
                    )
                
                character_name = character[1]
                
                # 获取源语音目录（带_Voices后缀）
                source_voices_dir = file_manager.get_voice_directory(character_name)
                
                # 检查源目录是否存在
                if not os.path.exists(source_voices_dir):
                    return (
                        gr.update(value=f"❌ 语音目录不存在: {source_voices_dir}", visible=True),
                        gr.update(visible=False)
                    )
                
                # 确保输出目录存在
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                
                # 进度回调函数
                def progress_callback(progress_value, message):
                    progress(progress_value, desc=message)
                
                # 执行导出
                result = voice_exporter.export_voice_pack(
                    character_name=character_name,
                    source_voices_dir=source_voices_dir,
                    output_dir=output_dir,
                    progress_callback=progress_callback
                )
                
                if result['success']:
                    stats = result['stats']
                    success_msg = (
                        f"✅ 语音包导出成功！\n"
                        f"📁 文件位置: {result['zip_path']}\n"
                        f"📊 处理统计: {stats['success_count']}/{stats['total_count']} 文件成功转换"
                    )
                    
                    if stats['errors']:
                        success_msg += f"\n⚠️ 警告: {len(stats['errors'])} 个文件处理失败"
                    
                    return (
                        gr.update(value=success_msg, visible=True),
                        gr.update(value=result['zip_path'], visible=True)
                    )
                else:
                    error_msg = f"❌ 导出失败: {result['message']}"
                    if result['stats']['errors']:
                        error_msg += f"\n错误详情:\n" + "\n".join(result['stats']['errors'][:5])
                        if len(result['stats']['errors']) > 5:
                            error_msg += f"\n... 还有 {len(result['stats']['errors']) - 5} 个错误"
                    
                    return (
                        gr.update(value=error_msg, visible=True),
                        gr.update(visible=False)
                    )
                    
            except Exception as e:
                error_msg = f"❌ 导出过程中发生错误: {str(e)}"
                return (
                    gr.update(value=error_msg, visible=True),
                    gr.update(visible=False)
                )

        # 绑定事件
        export_interface.load(get_characters, None, character_dropdown)
        
        # 角色选择变化时更新按钮状态
        character_dropdown.change(
            update_export_button_state,
            inputs=[character_dropdown],
            outputs=[export_button, status_text]
        )
        
        export_button.click(
            export_voice_pack_with_progress,
            inputs=[character_dropdown],
            outputs=[status_text, download_file],
            show_progress=True
        )

    return export_interface


if __name__ == "__main__":
    db.initialize_database()

    iface = gr.TabbedInterface([
        character_ui(),
        llm_config_ui(),
        build_dialogue_generation_ui(db),
        voice_generation_ui(),
        export_ui()
    ], ["角色管理", "LLM配置", "台词生成", "语音生成", "导出语音包"], title="breathVOICE：个性化角色语音定制系统")

    port = int(os.environ.get('GRADIO_SERVER_PORT', 7866))
    
    # 获取当前脚本所在目录，确保跨平台兼容性
    current_dir = os.path.dirname(os.path.abspath(__file__))
    characters_path = os.path.join(current_dir, 'Characters')
    
    iface.launch(
        inbrowser=True, 
        server_port=port, 
        share=False, 
        server_name="127.0.0.1",
        allowed_paths=[characters_path],
        app_kwargs={
            "docs_url": None,
            "redoc_url": None,
        },
        show_error=True,
        quiet=False
    )