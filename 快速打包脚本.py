#!/usr/bin/env python3
"""
breathVOICE 一键打包脚本
基于成功的打包经验，提供简化的打包流程
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🚀 breathVOICE 一键打包工具")
    print("=" * 60)

def check_environment():
    """检查打包环境"""
    print("🔍 检查打包环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major != 3 or python_version.minor < 8:
        print(f"❌ Python版本不兼容: {python_version.major}.{python_version.minor}")
        return False
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要文件
    required_files = ['app_standalone.py', 'database.py', 'file_manager.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return False
    print("✅ 必要文件检查通过")
    
    return True

def install_dependencies():
    """安装打包依赖"""
    print("📦 安装打包依赖...")
    
    try:
        # 检查PyInstaller是否已安装
        subprocess.run([sys.executable, '-c', 'import PyInstaller'], 
                      check=True, capture_output=True)
        print("✅ PyInstaller已安装")
    except subprocess.CalledProcessError:
        print("📥 安装PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                      check=True)
        print("✅ PyInstaller安装完成")

def clean_build_files():
    """清理构建文件"""
    print("🧹 清理旧的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  删除目录: {dir_name}")
    
    # 清理spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  删除文件: {spec_file}")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # 构建命令 (基于成功的经验)
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', 'breathVOICE',
        '--add-data', 'assets:assets',
        '--add-data', 'Characters:Characters',
        '--hidden-import', 'gradio',
        '--hidden-import', 'pandas',
        '--hidden-import', 'numpy',
        '--hidden-import', 'soundfile',
        '--hidden-import', 'openai',
        '--hidden-import', 'requests',
        '--hidden-import', 'tqdm',
        '--hidden-import', 'PIL',
        'app_standalone.py'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print("错误输出:", e.stderr)
        return False

def check_build_result():
    """检查构建结果"""
    print("🔍 检查构建结果...")
    
    exe_path = Path('dist/breathVOICE')
    if not exe_path.exists():
        print("❌ 可执行文件未生成")
        return False
    
    file_size = exe_path.stat().st_size
    size_mb = file_size / (1024 * 1024)
    print(f"✅ 可执行文件生成成功")
    print(f"  文件路径: {exe_path}")
    print(f"  文件大小: {size_mb:.1f} MB")
    
    return True

def create_launcher_script():
    """创建启动脚本"""
    print("📝 创建启动脚本...")
    
    # Windows批处理脚本
    bat_content = '''@echo off
echo 启动 breathVOICE...
echo 请等待应用加载完成后，浏览器将自动打开
echo 访问地址: http://localhost:7866
echo.
echo 按 Ctrl+C 停止应用
echo.
.\\dist\\breathVOICE.exe
pause
'''
    
    with open('启动breathVOICE.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    # macOS/Linux shell脚本
    sh_content = '''#!/bin/bash
echo "启动 breathVOICE..."
echo "请等待应用加载完成后，浏览器将自动打开"
echo "访问地址: http://localhost:7866"
echo ""
echo "按 Ctrl+C 停止应用"
echo ""
./dist/breathVOICE
'''
    
    with open('启动breathVOICE.sh', 'w', encoding='utf-8') as f:
        f.write(sh_content)
    
    # 设置执行权限
    os.chmod('启动breathVOICE.sh', 0o755)
    
    print("✅ 启动脚本创建完成")

def create_readme():
    """创建使用说明"""
    print("📖 创建使用说明...")
    
    readme_content = '''# breathVOICE 可执行文件使用说明

## 🚀 快速开始

### Windows用户
1. 双击 `启动breathVOICE.bat`
2. 等待应用启动 (约10-30秒)
3. 浏览器将自动打开应用界面

### macOS/Linux用户
1. 双击 `启动breathVOICE.sh` 或在终端运行 `./启动breathVOICE.sh`
2. 等待应用启动 (约10-30秒)
3. 手动打开浏览器访问: http://localhost:7866

## 📁 文件说明

- `dist/breathVOICE` - 主程序可执行文件
- `启动breathVOICE.bat` - Windows启动脚本
- `启动breathVOICE.sh` - macOS/Linux启动脚本
- `assets/` - 应用资源文件
- `Characters/` - 角色配置文件

## ⚠️ 注意事项

1. **首次启动较慢**: 第一次运行需要初始化，请耐心等待
2. **防火墙提示**: 系统可能询问网络访问权限，请允许
3. **端口占用**: 如果7866端口被占用，应用会自动选择其他端口
4. **停止应用**: 在终端按 Ctrl+C 或关闭浏览器标签页

## 🔧 故障排除

### 应用无法启动
- 检查是否有杀毒软件阻止
- 确保有足够的磁盘空间 (至少1GB)
- 尝试以管理员权限运行

### 浏览器无法访问
- 检查防火墙设置
- 尝试手动访问: http://localhost:7866
- 检查终端是否有错误信息

### 功能异常
- 重启应用
- 检查网络连接 (某些功能需要网络)
- 查看终端错误信息

## 📞 技术支持

如遇到问题，请提供以下信息：
- 操作系统版本
- 错误信息截图
- 终端输出日志

---
*生成时间: 自动生成*
'''
    
    with open('使用说明.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 使用说明创建完成")

def main():
    """主函数"""
    print_banner()
    
    try:
        # 检查环境
        if not check_environment():
            print("❌ 环境检查失败，请解决问题后重试")
            return False
        
        # 安装依赖
        install_dependencies()
        
        # 清理旧文件
        clean_build_files()
        
        # 构建可执行文件
        if not build_executable():
            print("❌ 构建失败")
            return False
        
        # 检查结果
        if not check_build_result():
            print("❌ 构建验证失败")
            return False
        
        # 创建辅助文件
        create_launcher_script()
        create_readme()
        
        print("\n" + "=" * 60)
        print("🎉 打包完成!")
        print("=" * 60)
        print("📁 生成的文件:")
        print("  - dist/breathVOICE (主程序)")
        print("  - 启动breathVOICE.bat (Windows启动脚本)")
        print("  - 启动breathVOICE.sh (macOS/Linux启动脚本)")
        print("  - 使用说明.md (详细说明)")
        print("\n🚀 运行方式:")
        print("  Windows: 双击 启动breathVOICE.bat")
        print("  macOS/Linux: 双击 启动breathVOICE.sh")
        print("  或直接运行: ./dist/breathVOICE")
        print("\n🌐 访问地址: http://localhost:7866")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        input("\n按回车键退出...")
        sys.exit(1)
    else:
        input("\n按回车键退出...")