#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版本的breathVOICE应用程序
用于测试基本功能，避免Gradio JSON schema错误
"""

import gradio as gr
import os

def simple_dialogue_generation(character_name, prompt_text):
    """简单的对话生成函数"""
    if not character_name or not prompt_text:
        return "请输入角色名称和提示文本"
    
    # 模拟对话生成
    result = f"角色: {character_name}\n提示: {prompt_text}\n\n生成的对话内容:\n这是一个测试对话，用于验证应用程序基本功能正常运行。"
    return result

def create_simple_interface():
    """创建简化的用户界面"""
    with gr.Blocks(title="breathVOICE - 简化版本") as interface:
        gr.Markdown("# breathVOICE 对话生成系统 - 简化版本")
        gr.Markdown("这是一个简化版本，用于测试基本功能。")
        
        with gr.Row():
            with gr.Column():
                character_input = gr.Textbox(
                    label="角色名称",
                    placeholder="请输入角色名称",
                    value="测试角色"
                )
                prompt_input = gr.Textbox(
                    label="提示文本",
                    placeholder="请输入对话提示",
                    lines=3,
                    value="请生成一段友好的问候语"
                )
                generate_btn = gr.Button("生成对话", variant="primary")
            
            with gr.Column():
                output_text = gr.Textbox(
                    label="生成结果",
                    lines=10,
                    interactive=False
                )
        
        # 事件绑定
        generate_btn.click(
            simple_dialogue_generation,
            inputs=[character_input, prompt_input],
            outputs=output_text
        )
    
    return interface

if __name__ == "__main__":
    # 创建简化界面
    app = create_simple_interface()
    
    # 启动应用程序
    port = int(os.environ.get('GRADIO_SERVER_PORT', 7866))
    app.launch(
        inbrowser=True, 
        server_port=port, 
        share=False,
        server_name="127.0.0.1"
    )