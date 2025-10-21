#!/usr/bin/env python3
"""
breathVOICE 独立版应用程序
专门为Windows EXE打包优化的版本
"""

import gradio as gr
import pandas as pd
import json
import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

# 获取应用程序目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe
    APP_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = sys._MEIPASS if hasattr(sys, '_MEIPASS') else APP_DIR
else:
    # 如果是开发环境
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = APP_DIR

# 设置工作目录
os.chdir(APP_DIR)

# 添加资源路径到sys.path
if RESOURCE_DIR not in sys.path:
    sys.path.insert(0, RESOURCE_DIR)

try:
    from database import CharacterDatabase
    from file_manager import CharacterFileManager
    from action_parameters import ALL_ACTION_PARAMS
    from dialogue_generation_ui_v2 import build_dialogue_generation_ui
    from voice_pack_exporter import VoicePackExporter
except ImportError as e:
    print(f"导入模块失败: {e}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"资源目录: {RESOURCE_DIR}")
    print(f"Python路径: {sys.path}")
    input("按回车键退出...")
    sys.exit(1)

import numpy as np
import soundfile as sf
import zipfile
from tqdm import tqdm

# 应用JSON Schema补丁以避免Gradio内部错误
import gradio_client.utils
original_json_schema_to_python_type = gradio_client.utils.json_schema_to_python_type

def patched_json_schema_to_python_type(schema):
    """修复Gradio JSON schema处理中的bool类型错误"""
    try:
        if isinstance(schema, bool):
            return str
        if not isinstance(schema, dict):
            return str
        return original_json_schema_to_python_type(schema)
    except (TypeError, AttributeError):
        return str

gradio_client.utils.json_schema_to_python_type = patched_json_schema_to_python_type

def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        'Characters',
        'voice_outputs',
        'assets',
        'flagged'
    ]
    
    for directory in directories:
        dir_path = os.path.join(APP_DIR, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"创建目录: {dir_path}")

def check_dependencies():
    """检查关键依赖是否可用"""
    try:
        import sqlite3
        import requests
        import openai
        print("✅ 核心依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 依赖检查失败: {e}")
        return False

def open_browser_delayed(url, delay=3):
    """延迟打开浏览器"""
    def open_browser():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"已在浏览器中打开: {url}")
        except Exception as e:
            print(f"无法自动打开浏览器: {e}")
            print(f"请手动访问: {url}")
    
    thread = threading.Thread(target=open_browser)
    thread.daemon = True
    thread.start()

# 初始化数据库和文件管理器
try:
    db = CharacterDatabase()
    file_manager = CharacterFileManager()
    print("✅ 数据库和文件管理器初始化成功")
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    input("按回车键退出...")
    sys.exit(1)

def get_language_encoding(language):
    """获取语言编码映射"""
    language_map = {
        "中文": "台词",
        "English": "英文台词", 
        "日本語": "日文台词"
    }
    return language_map.get(language, "台词")

def create_initial_df(dialogue_column):
    """创建初始数据框"""
    data = []
    for action_type, params in ALL_ACTION_PARAMS.items():
        for param in params:
            data.append({
                "动作类型": action_type,
                "参数": param["param"],
                "描述": param["description"],
                dialogue_column: ""
            })
    return pd.DataFrame(data)

def create_character(name, description, avatar_file):
    """创建角色"""
    if not name or not description:
        return "❌ 角色名称和描述不能为空", update_character_list()
    
    try:
        character_id = db.create_character(name, description)
        
        if avatar_file is not None:
            avatar_filename = file_manager.save_avatar(character_id, avatar_file)
            db.update_character_avatar(character_id, avatar_filename)
        
        return f"✅ 角色 '{name}' 创建成功！", update_character_list()
    except Exception as e:
        return f"❌ 创建角色失败: {str(e)}", update_character_list()

def update_character_list():
    """更新角色列表"""
    try:
        characters = db.get_all_characters()
        if not characters:
            return gr.Dropdown(choices=[], value=None, label="选择角色")
        
        choices = [(f"{char['name']} (ID: {char['id']})", char['id']) for char in characters]
        return gr.Dropdown(choices=choices, value=choices[0][1] if choices else None, label="选择角色")
    except Exception as e:
        print(f"更新角色列表失败: {e}")
        return gr.Dropdown(choices=[], value=None, label="选择角色")

def get_characters_for_update():
    """获取用于更新的角色列表"""
    return update_character_list()

def update_character_fields(character_id):
    """更新角色字段"""
    if not character_id:
        return "", "", None
    
    try:
        character = db.get_character(character_id)
        if character:
            avatar_path = None
            if character['avatar_filename']:
                avatar_path = file_manager.get_avatar_path(character_id, character['avatar_filename'])
                if not os.path.exists(avatar_path):
                    avatar_path = None
            
            return character['name'], character['description'], avatar_path
        else:
            return "", "", None
    except Exception as e:
        print(f"获取角色信息失败: {e}")
        return "", "", None

def character_ui():
    """角色管理界面"""
    with gr.Blocks() as interface:
        gr.Markdown("# 🎭 角色管理")
        gr.Markdown("创建和管理你的虚拟角色")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 创建新角色")
                name_input = gr.Textbox(label="角色名称", placeholder="输入角色名称...")
                description_input = gr.Textbox(
                    label="角色描述", 
                    lines=5, 
                    placeholder="详细描述角色的性格、背景、说话风格等..."
                )
                avatar_input = gr.File(
                    label="角色头像", 
                    file_types=["image"],
                    type="filepath"
                )
                create_btn = gr.Button("创建角色", variant="primary")
                create_output = gr.Textbox(label="创建结果", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("## 管理现有角色")
                character_dropdown = gr.Dropdown(label="选择角色", interactive=True)
                
                with gr.Group():
                    update_name = gr.Textbox(label="角色名称")
                    update_description = gr.Textbox(label="角色描述", lines=5)
                    update_avatar = gr.Image(label="当前头像", type="filepath")
                    new_avatar = gr.File(label="上传新头像", file_types=["image"], type="filepath")
                
                with gr.Row():
                    update_btn = gr.Button("更新角色", variant="secondary")
                    delete_btn = gr.Button("删除角色", variant="stop")
                
                update_output = gr.Textbox(label="操作结果", interactive=False)
        
        # 事件绑定
        create_btn.click(
            create_character,
            inputs=[name_input, description_input, avatar_input],
            outputs=[create_output, character_dropdown]
        )
        
        character_dropdown.change(
            update_character_fields,
            inputs=[character_dropdown],
            outputs=[update_name, update_description, update_avatar]
        )
        
        # 初始化角色列表
        interface.load(
            update_character_list,
            outputs=[character_dropdown]
        )
    
    return interface

def llm_config_ui():
    """LLM配置界面"""
    with gr.Blocks() as interface:
        gr.Markdown("# 🤖 LLM配置")
        gr.Markdown("配置大语言模型API用于台词生成")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## API配置")
                api_url = gr.Textbox(
                    label="API URL", 
                    placeholder="https://api.openai.com/v1",
                    info="必须以 /v1 结尾"
                )
                api_key = gr.Textbox(
                    label="API Key", 
                    type="password",
                    placeholder="输入你的API密钥..."
                )
                
                test_btn = gr.Button("测试连接", variant="secondary")
                save_btn = gr.Button("保存配置", variant="primary")
                
                result_output = gr.Textbox(label="测试结果", interactive=False)
            
            with gr.Column():
                gr.Markdown("## 使用说明")
                gr.Markdown("""
                ### 支持的API服务
                - OpenAI官方API
                - Azure OpenAI
                - 其他OpenAI兼容的API服务
                - 本地部署的LLM服务
                
                ### 配置要求
                1. API URL必须以 `/v1` 结尾
                2. API Key必须有效且有足够的配额
                3. 确保网络连接正常
                
                ### 注意事项
                - API Key将安全存储在本地
                - 建议使用专门的API Key
                - 定期检查API使用量
                """)
    
    return interface

def main():
    """主函数"""
    print("🎯 breathVOICE 独立版启动中...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    # 确保目录存在
    ensure_directories()
    
    # 初始化数据库
    try:
        db.initialize_database()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        input("按回车键退出...")
        return
    
    # 创建界面
    try:
        print("🎨 正在创建用户界面...")
        
        # 简化版界面，只包含核心功能
        iface = gr.TabbedInterface([
            character_ui(),
            llm_config_ui(),
        ], ["角色管理", "LLM配置"], title="breathVOICE：个性化角色语音定制系统")
        
        print("✅ 界面创建成功")
        
    except Exception as e:
        print(f"❌ 界面创建失败: {e}")
        input("按回车键退出...")
        return
    
    # 启动服务器
    try:
        port = int(os.environ.get('GRADIO_SERVER_PORT', 7866))
        server_url = f"http://localhost:{port}"
        
        print(f"🚀 正在启动服务器...")
        print(f"📍 访问地址: {server_url}")
        print("🌐 浏览器将自动打开，如未打开请手动访问上述地址")
        print("⚠️  关闭此窗口将停止程序")
        print("=" * 50)
        
        # 延迟打开浏览器
        open_browser_delayed(server_url)
        
        # 启动Gradio服务器
        iface.launch(
            inbrowser=False,  # 我们手动控制浏览器打开
            server_port=port,
            share=False,
            server_name="127.0.0.1",
            show_error=True,
            quiet=False,
            prevent_thread_lock=False
        )
        
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        input("按回车键退出...")
        return

if __name__ == "__main__":
    main()