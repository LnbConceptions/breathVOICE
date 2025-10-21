#!/usr/bin/env python3
"""
Gradio兼容性修复脚本
解决Gradio 5.x版本的兼容性问题
"""

import subprocess
import sys
import os

def check_gradio_version():
    """检查当前Gradio版本"""
    try:
        import gradio as gr
        version = gr.__version__
        print(f"当前Gradio版本: {version}")
        
        # 检查是否为5.x版本
        major_version = int(version.split('.')[0])
        if major_version >= 5:
            print("⚠️  检测到Gradio 5.x版本，可能存在兼容性问题")
            return True, version
        else:
            print("✅ Gradio版本兼容")
            return False, version
    except ImportError:
        print("❌ Gradio未安装")
        return False, None

def fix_gradio_compatibility():
    """修复Gradio兼容性问题"""
    print("🔧 开始修复Gradio兼容性问题...")
    
    try:
        # 卸载当前版本
        print("1. 卸载当前Gradio版本...")
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'gradio', 'gradio-client', '-y'], 
                      check=True)
        
        # 安装兼容版本
        print("2. 安装兼容版本...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'gradio>=4.44.0,<5.0.0', 
                       'gradio-client>=0.17.0,<1.0.0',
                       'pydantic>=2.0.0,<3.0.0'], 
                      check=True)
        
        print("✅ Gradio兼容性修复完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 修复失败: {e}")
        return False

def test_gradio_after_fix():
    """测试修复后的Gradio功能"""
    print("🧪 测试修复后的Gradio功能...")
    
    try:
        import gradio as gr
        print(f"新版本: {gr.__version__}")
        
        # 测试基本组件
        textbox = gr.Textbox(label="测试")
        button = gr.Button("测试按钮")
        
        # 测试界面创建
        def test_func(x):
            return f"输入: {x}"
        
        with gr.Blocks() as demo:
            input_box = gr.Textbox(label="输入")
            output_box = gr.Textbox(label="输出")
            btn = gr.Button("测试")
            btn.click(test_func, inputs=input_box, outputs=output_box)
        
        print("✅ Gradio功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Gradio功能测试失败: {e}")
        return False

def backup_current_environment():
    """备份当前环境"""
    print("💾 备份当前环境...")
    
    try:
        # 导出当前环境
        with open('environment_backup.txt', 'w') as f:
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                                  capture_output=True, text=True)
            f.write(result.stdout)
        
        print("✅ 环境备份完成: environment_backup.txt")
        return True
        
    except Exception as e:
        print(f"❌ 环境备份失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Gradio兼容性修复工具")
    print("=" * 50)
    
    # 备份环境
    backup_current_environment()
    
    # 检查版本
    needs_fix, current_version = check_gradio_version()
    
    if needs_fix:
        response = input("\n是否要修复Gradio兼容性问题？(y/n): ").lower().strip()
        if response == 'y':
            if fix_gradio_compatibility():
                test_gradio_after_fix()
            else:
                print("修复失败，请手动处理")
        else:
            print("用户取消修复")
    else:
        print("无需修复")
    
    print("\n修复完成！")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    finally:
        input("\n按回车键退出...")