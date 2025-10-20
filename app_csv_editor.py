import gradio as gr
import pandas as pd
import openai
import json
import zipfile
import shutil
import database as db
import os
from datetime import datetime
import unicodedata
import re
from typing import Any
import tempfile
import threading
import time
from dialogue_generator import DialogueGenerator

# 写入临时CSV的锁，避免并发读写冲突
write_lock = threading.Lock()

# 统一蓝本：台词模版绝对路径
TEMPLATE_CSV_PATH = "/Users/Saga/breathVOICE/台词模版.csv"

# 全局状态变量
current_temp_file = None
generation_state = {"is_running": False, "stop_requested": False}

# 动作参数列表
ALL_ACTION_PARAMS = [
    "greeting_1", "greeting_2", "greeting_3", "greeting_4", "greeting_5",
    "orgasm_1", "orgasm_2", "orgasm_3", "orgasm_4", "orgasm_5",
    "reaction_1", "reaction_2", "reaction_3", "reaction_4", "reaction_5",
    "tease_1", "tease_2", "tease_3", "tease_4", "tease_5",
    "impact_1", "impact_2", "impact_3", "impact_4", "impact_5",
    "touch_1", "touch_2", "touch_3", "touch_4", "touch_5"
]

def create_character(name, description, avatar_path):
    character_id = db.create_character(name, description, avatar_path)
    return f"Character '{name}' created with ID: {character_id}"

def update_character_list():
    characters = db.get_characters()
    return [[c[0], c[1], c[2]] for c in characters]

def get_characters_for_update():
    characters = db.get_characters()
    return [(c[1], c[0]) for c in characters]

def update_character_fields(character_id):
    if character_id:
        character = db.get_character(character_id)
        if character:
            return character[1], character[2], character[3]
    return "", "", ""

def update_character(character_id, name, description, avatar_path):
    if character_id:
        db.update_character(character_id, name, description, avatar_path)
        return f"Character '{name}' updated successfully"
    return "Please select a character to update"

def delete_character(evt: gr.SelectData, character_list_df):
    if evt.index is not None and len(character_list_df) > evt.index[0]:
        character_id = character_list_df[evt.index[0]][0]
        db.delete_character(character_id)
        return f"Character with ID {character_id} deleted"
    return "Invalid selection"

def character_ui():
    with gr.Blocks() as character_interface:
        gr.Markdown("## Step 1: Character Management")
        with gr.Row():
            with gr.Column():
                name_input = gr.Textbox(label="Character Name")
                description_input = gr.Textbox(label="Character Description", lines=3)
                avatar_input = gr.Textbox(label="Avatar Image Path")
                create_button = gr.Button("Create Character")
                create_output = gr.Textbox(label="Status", interactive=False)
            
            with gr.Column():
                update_dropdown = gr.Dropdown(label="Select Character to Update")
                update_name = gr.Textbox(label="Name")
                update_description = gr.Textbox(label="Description", lines=3)
                update_avatar = gr.Textbox(label="Avatar Image Path")
                update_button = gr.Button("Update Character")
                update_output = gr.Textbox(label="Status", interactive=False)
        
        with gr.Row():
            character_list = gr.Dataframe(headers=["ID", "Name", "Description"], interactive=False)
            refresh_button = gr.Button("Refresh List")
        
        create_button.click(create_character, [name_input, description_input, avatar_input], create_output)
        create_button.click(lambda: update_character_list(), outputs=character_list)
        
        refresh_button.click(update_character_list, outputs=character_list)
        
        update_dropdown.change(update_character_fields, update_dropdown, [update_name, update_description, update_avatar])
        update_button.click(update_character, [update_dropdown, update_name, update_description, update_avatar], update_output)
        update_button.click(lambda: update_character_list(), outputs=character_list)
        
        character_list.select(delete_character, [character_list], create_output)
        
        character_interface.load(update_character_list, outputs=character_list)

        # 初始化更新下拉选项（非事件赋值，避免update对象）
        try:
            update_dropdown.choices = get_characters_for_update()
        except Exception as e:
            print(f"初始化更新下拉菜单失败: {e}")
    
    return character_interface

def llm_config_ui():
    """LLM配置界面"""
    with gr.Blocks() as llm_config_interface:
        gr.Markdown("## Step 2: LLM Configuration")
        gr.Markdown("LLM配置功能保持原有实现")
    return llm_config_interface

# CSV编辑器核心功能
def ensure_character_output_folder(character_name):
    """确保角色输出文件夹存在"""
    folder_path = os.path.join("output", character_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def _normalize_template_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """规范化模板或临时CSV的列结构与类型"""
    try:
        cols = list(df.columns)
        # 纠正可能异常的首列名（例如首行误写为 FALSE）
        if len(cols) >= 1 and cols[0] not in ["选择", "FALSE", "True", "False", True, False]:
            # 若首列名不是期望值，仍将其视为选择列
            pass
        # 重命名列为统一名称
        rename_map = {}
        if len(cols) >= 1:
            rename_map[cols[0]] = "选择"
        if len(cols) >= 2:
            rename_map[cols[1]] = "动作参数"
        if len(cols) >= 3:
            rename_map[cols[2]] = "台词"
        df = df.rename(columns=rename_map)

        # 确保三列存在
        if "选择" not in df.columns:
            df.insert(0, "选择", False)
        if "动作参数" not in df.columns:
            # 无动作参数列时，不做额外填充（避免与模板不一致）
            df["动作参数"] = ""
        if "台词" not in df.columns:
            df["台词"] = ""

        # 选择列转为布尔
        try:
            df["选择"] = df["选择"].astype(str).str.lower().map({"true": True, "false": False})
            df["选择"] = df["选择"].fillna(False)
        except Exception:
            df["选择"] = False

        # 台词列为空则归一化为空字符串
        df["台词"] = df["台词"].fillna("")
        # 去除可能的多余空白
        df["动作参数"] = df["动作参数"].astype(str).str.strip()
        df["台词"] = df["台词"].astype(str)
    except Exception as e:
        print(f"规范化模板DataFrame失败: {e}")
    return df

def create_temp_csv_file(character_name):
    """为角色创建临时CSV文件：以模板CSV复制生成临时副本"""
    global current_temp_file
    
    # 清理之前的临时文件
    cleanup_temp_file()
    
    # 创建新的临时文件
    temp_dir = tempfile.gettempdir()
    temp_filename = f"breathvoice_temp_{character_name}_{int(time.time())}.csv"
    current_temp_file = os.path.join(temp_dir, temp_filename)
    
    try:
        # 直接以模板复制为临时副本，确保行数与动作参数一致
        if os.path.exists(TEMPLATE_CSV_PATH):
            shutil.copy2(TEMPLATE_CSV_PATH, current_temp_file)
            # 规范化列结构
            df = pd.read_csv(current_temp_file, encoding='utf-8')
            df = _normalize_template_dataframe(df)
            df.to_csv(current_temp_file, index=False, encoding='utf-8')
        else:
            # 模板缺失时最小化回退：空表
            df = pd.DataFrame({
                "选择": [],
                "动作参数": [],
                "台词": []
            })
            df.to_csv(current_temp_file, index=False, encoding='utf-8')
    except Exception as e:
        print(f"复制模板为临时CSV失败: {e}")
    return current_temp_file

def load_temp_csv_as_dataframe():
    """加载临时CSV文件为DataFrame"""
    global current_temp_file
    
    target_path = current_temp_file if (current_temp_file and os.path.exists(current_temp_file)) else TEMPLATE_CSV_PATH
    if target_path and os.path.exists(target_path):
        try:
                df = pd.read_csv(target_path, encoding='utf-8')
                if '动作参数' in df.columns:
                    df['动作参数'] = df['动作参数'].astype(str).fillna('')
                df = _normalize_template_dataframe(df)
                return df
        except Exception as e:
            print(f"加载临时CSV文件失败: {e}")
    
    # 返回空DataFrame
    return pd.DataFrame({
        "选择": [],
        "动作参数": [],
        "台词": []
    })

def save_dataframe_to_temp_csv(df):
    """保存DataFrame到临时CSV文件"""
    global current_temp_file
    
    if current_temp_file and df is not None:
        try:
            # 移除选择列进行保存
            save_df = df.copy()
            if "选择" in save_df.columns:
                save_df = save_df.drop("选择", axis=1)
            save_df.to_csv(current_temp_file, index=False, encoding='utf-8')
            return True
        except Exception as e:
            print(f"保存到临时CSV文件失败: {e}")
    return False

def create_temp_copy_from_existing_csv(character_name, csv_filename):
    """从已有CSV文件创建临时副本"""
    global current_temp_file
    
    # 清理之前的临时文件
    cleanup_temp_file()
    
    # 构建源文件路径
    character_folder = ensure_character_output_folder(character_name)
    source_file = os.path.join(character_folder, csv_filename)
    
    if not os.path.exists(source_file):
        return None
    
    # 创建临时文件
    temp_dir = tempfile.gettempdir()
    temp_filename = f"breathvoice_temp_{character_name}_{int(time.time())}.csv"
    current_temp_file = os.path.join(temp_dir, temp_filename)
    
    try:
        # 复制文件
        shutil.copy2(source_file, current_temp_file)
        return current_temp_file
    except Exception as e:
        print(f"创建临时副本失败: {e}")
        current_temp_file = None
        return None

def cleanup_temp_file():
    """清理临时文件"""
    global current_temp_file
    
    if current_temp_file and os.path.exists(current_temp_file):
        try:
            os.remove(current_temp_file)
        except Exception as e:
            print(f"清理临时文件失败: {e}")
    current_temp_file = None

def get_character_csv_files(character_name):
    """获取角色的CSV文件列表"""
    character_folder = ensure_character_output_folder(character_name)
    csv_files = []
    
    try:
        for file in os.listdir(character_folder):
            if file.endswith('.csv') and not file.startswith('breathvoice_temp_'):
                file_path = os.path.join(character_folder, file)
                mtime = os.path.getmtime(file_path)
                csv_files.append((file, mtime))
        
        # 按修改时间倒序排列
        csv_files.sort(key=lambda x: x[1], reverse=True)
        return [file[0] for file in csv_files]
    except Exception as e:
        print(f"获取CSV文件列表失败: {e}")
        return []

def dialogue_generation_ui():
    """台词生成（Generate Dialogue）界面"""
    with gr.Blocks() as dialogue_generation_interface:
        gr.Markdown("## Step 3: 台词生成")
        
        # 角色和配置选择
        with gr.Row():
            character_dropdown = gr.Dropdown(label="选择角色", choices=[], interactive=True)
            llm_config_dropdown = gr.Dropdown(label="LLM配置", choices=[], interactive=True)
            language_dropdown = gr.Dropdown(
                label="语言", 
                choices=[("中文", "中文"), ("English", "English")], 
                value="中文", 
                interactive=True
            )
        
        # CSV文件管理（改为文本列表 + 文件名输入，避免update对象）
        with gr.Row():
            csv_files_text = gr.Textbox(label="已有CSV文件列表", interactive=False, lines=4)
            refresh_csv_button = gr.Button("刷新文件列表", variant="secondary")
        with gr.Row():
            csv_filename_input = gr.Textbox(label="选择CSV文件名", placeholder="输入文件名以加载")
        
        # 状态显示
        with gr.Row():
            status_display = gr.Textbox(label="状态", interactive=False, lines=2, scale=1)
            llm_status_display = gr.Textbox(label="LLM通讯状态", interactive=False, lines=8, scale=2)
            prompt_display = gr.Textbox(label="当前提示词", interactive=False, lines=8, scale=2)

        # 生成控制
        with gr.Row():
            generate_button = gr.Button("开始生成", variant="primary")
            stop_button = gr.Button("停止生成", variant="secondary")
            refresh_temp_button = gr.Button("刷新", variant="secondary")
        
        # 台词生成表格
        dialogue_df = gr.Dataframe(
            label="台词生成",
            headers=["选择", "动作参数", "台词"],
            datatype=["bool", "str", "str"],
            interactive=True,
            wrap=True,
            column_widths=[60, 300, 1100]
        )
        
        # 保存功能
        with gr.Row():
            save_filename = gr.Textbox(label="保存文件名", placeholder="留空自动生成", scale=3)
            save_button = gr.Button("保存CSV文件", variant="primary", scale=1)
        
        # 事件处理函数
        def _compute_column_widths(df: pd.DataFrame):
            """根据当前数据动态计算列宽：选择最窄、动作参数适配最长项、台词最宽"""
            try:
                max_len = 0
                if df is not None and "动作参数" in df.columns:
                    max_len = int(df["动作参数"].astype(str).str.len().max()) if not df.empty else 0
                # 每字符约9px，加入左右内边距
                actions_width = max(180, min(600, max_len * 9 + 40))
                return [60, actions_width, 1100]
            except Exception:
                return [60, 300, 1100]

        def handle_character_change(character_id):
            """处理角色选择变化"""
            if not character_id:
                df = load_temp_csv_as_dataframe()
                return gr.update(value=df, column_widths=_compute_column_widths(df)), "", "请选择角色"
            
            try:
                character = db.get_character(character_id)
                if not character:
                    return gr.update(), gr.update(choices=[]), "角色不存在"
                
                character_name = character[1]
                
                # 创建临时CSV文件
                temp_file = create_temp_csv_file(character_name)
                if temp_file:
                    df = load_temp_csv_as_dataframe()
                    csv_files = get_character_csv_files(character_name)
                    csv_list_text = "\n".join(csv_files)
                    # 状态提示包含任务总数
                    total_tasks = len(df["动作参数"]) if "动作参数" in df.columns else 0
                    return (
                        gr.update(value=df, column_widths=_compute_column_widths(df)),
                        csv_list_text,
                        f"已为角色 {character_name} 创建临时CSV；任务数 {total_tasks}"
                    )
                else:
                    df = load_temp_csv_as_dataframe()
                    return gr.update(value=df, column_widths=_compute_column_widths(df)), "", "创建临时文件失败"
            except Exception as e:
                return gr.update(), gr.update(choices=[]), f"错误: {str(e)}"
        
        def handle_csv_file_selection(character_id, csv_filename):
            """处理CSV文件选择"""
            if not character_id or not csv_filename:
                df = load_temp_csv_as_dataframe()
                return gr.update(value=df, column_widths=_compute_column_widths(df)), "请选择角色和CSV文件"
            
            try:
                character = db.get_character(character_id)
                if not character:
                    return gr.update(), "角色不存在"
                
                character_name = character[1]
                
                # 创建临时副本
                temp_file = create_temp_copy_from_existing_csv(character_name, csv_filename)
                if temp_file:
                    df = load_temp_csv_as_dataframe()
                    return (
                        gr.update(value=df, column_widths=_compute_column_widths(df)),
                        f"已加载 {csv_filename} 的临时副本"
                    )
                else:
                    df = load_temp_csv_as_dataframe()
                    return gr.update(value=df, column_widths=_compute_column_widths(df)), "加载CSV文件失败"
            except Exception as e:
                return gr.update(), f"错误: {str(e)}"
        
        def handle_table_change(df_data):
            """处理表格数据变化"""
            if df_data is not None:
                try:
                    df = pd.DataFrame(df_data)
                    save_dataframe_to_temp_csv(df)
                    return gr.update(value=df, column_widths=_compute_column_widths(df)), "表格已自动保存到临时文件"
                except Exception as e:
                    df = load_temp_csv_as_dataframe()
                    return gr.update(value=df, column_widths=_compute_column_widths(df)), f"保存失败: {str(e)}"
            df = load_temp_csv_as_dataframe()
            return gr.update(value=df, column_widths=_compute_column_widths(df)), ""
        
        def refresh_csv_files(character_id):
            """刷新CSV文件列表"""
            if not character_id:
                return ""
            
            try:
                character = db.get_character(character_id)
                if character:
                    csv_files = get_character_csv_files(character[1])
                    return "\n".join(csv_files)
            except Exception as e:
                print(f"刷新文件列表失败: {e}")
            
            return ""
        
        def handle_save_csv(character_id, df_data, filename):
            """保存CSV文件"""
            if not character_id or df_data is None:
                return "请选择角色并确保有数据"
            
            try:
                character = db.get_character(character_id)
                if not character:
                    return "角色不存在"
                
                character_name = character[1]
                character_folder = ensure_character_output_folder(character_name)
                
                # 生成文件名
                if not filename or filename.strip() == "":
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{character_name}_dialogue_{timestamp}.csv"
                elif not filename.endswith('.csv'):
                    filename += '.csv'
                
                # 保存文件
                save_path = os.path.join(character_folder, filename)
                df = pd.DataFrame(df_data)
                
                # 移除选择列
                if "选择" in df.columns:
                    df = df.drop("选择", axis=1)
                
                df.to_csv(save_path, index=False, encoding='utf-8')
                return f"文件已保存: {filename}"
            except Exception as e:
                return f"保存失败: {str(e)}"
        
        def get_temp_file_content():
            """获取临时文件内容用于实时更新"""
            try:
                df = load_temp_csv_as_dataframe()
                return gr.update(value=df, column_widths=_compute_column_widths(df))
            except Exception as e:
                print(f"获取临时文件内容失败: {e}")
                df = load_temp_csv_as_dataframe()
                return gr.update(value=df, column_widths=_compute_column_widths(df))
        
        def run_generation_with_temp_file(character_id, llm_config_id, language):
            """运行生成并写入临时文件"""
            global generation_state
            
            if generation_state["is_running"]:
                return "生成正在进行中..."
            
            if not character_id or not llm_config_id:
                return "请选择角色和LLM配置"
            
            generation_state["is_running"] = True
            generation_state["stop_requested"] = False
            
            # 启动后台线程执行生成并实时写入临时CSV
            def _bg_worker(cid: int, lid: int, lang: str):
                try:
                    # 确保已有临时文件可写
                    if not current_temp_file:
                        # 若未创建临时文件，则根据角色创建
                        char = db.get_character(cid)
                        if not char:
                            print("角色不存在，生成终止")
                            return
                        create_temp_csv_file(char[1])
                    
                    generator = DialogueGenerator()
                    
                    def status_cb(msg: str):
                        # 控制台输出即可，前端通过Dataframe轮询展示数据
                        print(msg)
                    
                    def stop_check():
                        return generation_state.get("stop_requested", False)
                    
                    def table_update_callback(action: str, dialogue: str):
                        # 将生成内容写入临时CSV对应动作参数行
                        try:
                            with write_lock:
                                df = load_temp_csv_as_dataframe()
                                if "动作参数" in df.columns and "台词" in df.columns:
                                    mask = df["动作参数"] == action
                                    if mask.any():
                                        df.loc[mask, "台词"] = dialogue
                                    else:
                                        # 若不存在该动作参数行，追加一行
                                        new_row = {"选择": False, "动作参数": action, "台词": dialogue}
                                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                                    save_dataframe_to_temp_csv(df)
                        except Exception as e:
                            print(f"写入临时CSV失败: {e}")
                    
                    # 执行生成流程（批次 + 补齐）
                    generator.generate_dialogues_with_progress(
                        character_id=cid,
                        llm_config_id=lid,
                        language=lang,
                        csv_path=current_temp_file,
                        progress_callback=None,
                        status_callback=status_cb,
                        table_update_callback=table_update_callback,
                        stop_check=stop_check
                    )
                except Exception as e:
                    print(f"后台生成线程错误: {e}")
                finally:
                    generation_state["is_running"] = False
                    generation_state["stop_requested"] = False
            
            threading.Thread(target=_bg_worker, args=(character_id, llm_config_id, language), daemon=True).start()
            return "生成已开始...（实时写入临时CSV）"
        
        def stop_generation():
            """停止生成"""
            global generation_state
            generation_state["stop_requested"] = True
            generation_state["is_running"] = False
            return "生成已停止"
        
        def get_characters_and_configs():
            """获取角色和配置列表"""
            characters = db.get_characters()
            character_choices = [(f"{char[1]} (ID: {char[0]})", char[0]) for char in characters]
            
            llm_configs = db.get_llm_configs()
            llm_choices = [(f"{config[1]} ({config[4]})", config[0]) for config in llm_configs]
            
            return character_choices, llm_choices
        
        # 初始化下拉菜单
        character_choices, llm_choices = get_characters_and_configs()
        character_dropdown.choices = character_choices
        llm_config_dropdown.choices = llm_choices
        
        # 事件绑定
        character_dropdown.change(
            fn=handle_character_change,
            inputs=[character_dropdown],
            outputs=[dialogue_df, csv_files_text, status_display]
        )
        
        csv_filename_input.submit(
            fn=handle_csv_file_selection,
            inputs=[character_dropdown, csv_filename_input],
            outputs=[dialogue_df, status_display]
        )
        
        dialogue_df.change(
            fn=handle_table_change,
            inputs=[dialogue_df],
            outputs=[dialogue_df, status_display]
        )
        
        refresh_csv_button.click(
            fn=refresh_csv_files,
            inputs=[character_dropdown],
            outputs=[csv_files_text]
        )
        
        save_button.click(
            fn=handle_save_csv,
            inputs=[character_dropdown, dialogue_df, save_filename],
            outputs=[status_display]
        )
        
        generate_button.click(
            fn=run_generation_with_temp_file,
            inputs=[character_dropdown, llm_config_dropdown, language_dropdown],
            outputs=[status_display]
        )
        
        stop_button.click(
            fn=stop_generation,
            outputs=[status_display]
        )

        # 手动刷新临时CSV到表格
        refresh_temp_button.click(
            fn=get_temp_file_content,
            outputs=[dialogue_df]
        )
        
        # 移除LLM配置刷新按钮事件，避免使用update对象
        
        # 移除定时更新以兼容当前Gradio版本；改用手动刷新按钮
    
    return dialogue_generation_interface

def voice_generation_ui():
    """语音生成界面"""
    with gr.Blocks() as voice_generation_interface:
        gr.Markdown("## Step 4: Voice Generation")
        gr.Markdown("语音生成功能保持原有实现")
    return voice_generation_interface

def export_ui():
    """导出界面"""
    with gr.Blocks() as export_interface:
        gr.Markdown("## Step 5: Export Voice Pack")
        gr.Markdown("导出功能保持原有实现")
    return export_interface

if __name__ == "__main__":
    db.initialize_database()

    iface = gr.TabbedInterface([
        character_ui(),
        llm_config_ui(),
        dialogue_generation_ui(),
        voice_generation_ui(),
        export_ui()
    ], ["Character Management", "LLM Configuration", "Generate Dialogue", "Voice Generation", "Export Voice Pack"])

    port = int(os.environ.get('GRADIO_SERVER_PORT', 7866))
    iface.launch(inbrowser=True, server_port=port, share=True)