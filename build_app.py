#!/usr/bin/env python3
"""
breathVOICE macOS App 构建脚本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """清理之前的构建文件"""
    print("🧹 清理之前的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   删除: {dir_name}")
    
    # 清理.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    return True

def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查依赖...")
    
    try:
        import PyInstaller
        print(f"   ✅ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("   ❌ PyInstaller 未安装")
        return False
    
    try:
        import gradio
        print(f"   ✅ Gradio: {gradio.__version__}")
    except ImportError:
        print("   ❌ Gradio 未安装")
        return False
    
    # 检查图标文件
    icon_path = Path('icon/breathVOICE.icns')
    if icon_path.exists():
        print(f"   ✅ 图标文件: {icon_path}")
    else:
        print(f"   ❌ 图标文件不存在: {icon_path}")
        return False
    
    return True

def build_app():
    """构建macOS应用"""
    print("🔨 开始构建 breathVOICE.app...")
    
    # 运行PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'breathVOICE.spec'
    ]
    
    print(f"   执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ 构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 构建失败: {e}")
        print(f"   错误输出: {e.stderr}")
        return False

def post_build_setup():
    """构建后的设置"""
    print("⚙️  执行构建后设置...")
    
    app_path = Path('dist/breathVOICE.app')
    if not app_path.exists():
        print("   ❌ 应用包不存在")
        return False
    
    # 设置应用权限
    try:
        subprocess.run(['chmod', '+x', str(app_path / 'Contents/MacOS/breathVOICE')], check=True)
        print("   ✅ 设置执行权限")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  设置权限失败: {e}")
    
    # 显示应用信息
    app_size = get_dir_size(app_path)
    print(f"   📦 应用大小: {app_size:.1f} MB")
    print(f"   📍 应用路径: {app_path.absolute()}")
    
    return True

def get_dir_size(path):
    """获取目录大小（MB）"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)

def main():
    """主函数"""
    print("🚀 breathVOICE macOS App 构建器")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('app.py'):
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 执行构建步骤
    steps = [
        ("清理构建文件", clean_build),
        ("检查依赖", check_dependencies),
        ("构建应用", build_app),
        ("构建后设置", post_build_setup),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        if not step_func():
            print(f"❌ {step_name} 失败")
            sys.exit(1)
    
    print("\n🎉 构建完成!")
    print("=" * 50)
    print("📱 您的 breathVOICE.app 已准备就绪!")
    print("📂 位置: dist/breathVOICE.app")
    print("💡 您可以将应用拖拽到 Applications 文件夹中")

if __name__ == "__main__":
    main()