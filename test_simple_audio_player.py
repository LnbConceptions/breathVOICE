#!/usr/bin/env python3
"""
测试简化音频播放器UI的独立脚本
"""

import gradio as gr
import os

def create_simple_audio_demo():
    """创建简化音频播放器的演示界面"""
    
    # 自定义CSS样式，简化音频播放器
    css = """
    .simple-audio-player audio {
        height: 32px !important;
        border-radius: 6px !important;
    }
    .simple-audio-player .audio-container {
        padding: 4px !important;
    }
    .simple-audio-player .audio-waveform {
        display: none !important;
    }
    .comparison-section {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    """
    
    with gr.Blocks(css=css, title="简化音频播放器测试") as demo:
        gr.Markdown("# 音频播放器UI对比测试")
        gr.Markdown("这个演示展示了简化前后的音频播放器UI差异")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🎯 简化后的播放器（推荐）")
                with gr.Group(elem_classes=["comparison-section"]):
                    gr.Markdown("**特点：**")
                    gr.Markdown("- 更紧凑的高度（32px）")
                    gr.Markdown("- 隐藏了波形显示")
                    gr.Markdown("- 移除了下载和分享按钮")
                    gr.Markdown("- 更简洁的容器样式")
                    
                    # 简化的音频播放器
                    simple_audio = gr.Audio(
                        label="简化播放器", 
                        value=None, 
                        interactive=False, 
                        show_label=True,
                        show_download_button=False,
                        show_share_button=False,
                        waveform_options={"show_controls": False, "show_recording_waveform": False},
                        container=False,
                        elem_classes=["simple-audio-player"]
                    )
            
            with gr.Column():
                gr.Markdown("## 📊 标准播放器（对比）")
                with gr.Group(elem_classes=["comparison-section"]):
                    gr.Markdown("**特点：**")
                    gr.Markdown("- 标准高度（较高）")
                    gr.Markdown("- 显示波形")
                    gr.Markdown("- 包含所有默认按钮")
                    gr.Markdown("- 完整的控件界面")
                    
                    # 标准的音频播放器
                    standard_audio = gr.Audio(
                        label="标准播放器", 
                        value=None, 
                        interactive=False, 
                        show_label=True
                    )
        
        gr.Markdown("---")
        
        # 模拟台词列表的效果
        gr.Markdown("## 📝 在台词列表中的效果预览")
        gr.Markdown("以下模拟了在语音生成界面中的实际使用效果：")
        
        # 表头
        with gr.Row():
            gr.HTML("<div style='width: 32px; text-align: center; font-weight: bold;'>选择</div>")
            gr.HTML("<div style='flex: 3; text-align: center; font-weight: bold;'>动作参数</div>")
            gr.HTML("<div style='flex: 6; text-align: center; font-weight: bold;'>台词</div>")
            gr.HTML("<div style='flex: 3; text-align: center; font-weight: bold;'>音频</div>")
        
        # 模拟几行台词数据
        sample_data = [
            ("greeting_1", "你好，欢迎来到这里！"),
            ("reaction_1", "哇，这真是太棒了！"),
            ("tease_1", "你想要什么呢？"),
        ]
        
        for i, (action, dialogue) in enumerate(sample_data):
            with gr.Row():
                checkbox = gr.Checkbox(
                    label="", 
                    value=True, 
                    scale=0, 
                    min_width=32, 
                    show_label=False
                )
                action_param = gr.Textbox(
                    label="", 
                    value=action, 
                    interactive=False, 
                    scale=3, 
                    show_label=False
                )
                text = gr.Textbox(
                    label="", 
                    value=dialogue, 
                    interactive=False, 
                    scale=6, 
                    show_label=False
                )
                # 使用简化的音频播放器
                audio = gr.Audio(
                    label="", 
                    value=None, 
                    interactive=False, 
                    scale=3, 
                    show_label=False,
                    show_download_button=False,
                    show_share_button=False,
                    waveform_options={"show_controls": False, "show_recording_waveform": False},
                    container=False,
                    elem_classes=["simple-audio-player"]
                )
        
        gr.Markdown("---")
        gr.Markdown("💡 **说明：** 简化后的播放器更适合在台词列表中使用，因为它：")
        gr.Markdown("- 占用更少的垂直空间")
        gr.Markdown("- 界面更加整洁")
        gr.Markdown("- 专注于播放功能，移除了不必要的控件")
        gr.Markdown("- 在大量台词列表中提供更好的浏览体验")
    
    return demo

if __name__ == "__main__":
    demo = create_simple_audio_demo()
    demo.launch(
        inbrowser=True,
        server_port=7867,
        share=False,
        server_name="127.0.0.1",
        show_error=True
    )