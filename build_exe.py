#!/usr/bin/env python3
"""
breathVOICE Windows EXE 打包脚本
使用PyInstaller将项目打包为独立的Windows可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 需要包含的数据文件
datas = [
    ('assets', 'assets'),
    ('icon', 'icon'),
    ('Characters', 'Characters'),
    ('voice_outputs', 'voice_outputs'),
    ('*.csv', '.'),
    ('*.md', '.'),
    ('*.txt', '.'),
]

# 需要包含的隐藏导入
hiddenimports = [
    'gradio',
    'gradio.components',
    'gradio.interface',
    'gradio.blocks',
    'gradio.routes',
    'gradio.utils',
    'gradio_client',
    'gradio_client.utils',
    'pandas',
    'numpy',
    'soundfile',
    'sqlite3',
    'json',
    'csv',
    'threading',
    'queue',
    'requests',
    'openai',
    'PIL',
    'PIL.Image',
    'tqdm',
    'zipfile',
    'io',
    'base64',
    'datetime',
    'pathlib',
    'shutil',
    'tempfile',
    'uvicorn',
    'fastapi',
    'starlette',
    'pydantic',
    'websockets',
    'httpx',
    'anyio',
    'sniffio',
    'h11',
    'typing_extensions',
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'test',
        'tests',
        'unittest',
        'doctest',
        'pdb',
        'pydoc',
        'email',
        'xml',
        'xmlrpc',
        'urllib3',
        'http.server',
        'wsgiref',
        'multiprocessing',
        'concurrent.futures',
        'asyncio',
        'ssl',
        'socket',
        'socketserver',
        'ftplib',
        'poplib',
        'imaplib',
        'nntplib',
        'smtplib',
        'telnetlib',
        'uuid',
        'secrets',
        'hmac',
        'hashlib',
        'crypt',
        'getpass',
        'curses',
        'readline',
        'rlcompleter',
        'cmd',
        'shlex',
        'subprocess',
        'threading',
        'queue',
        '_thread',
        'dummy_threading',
        'sched',
        'profile',
        'pstats',
        'cProfile',
        'trace',
        'tracemalloc',
        'faulthandler',
        'pyclbr',
        'py_compile',
        'compileall',
        'dis',
        'pickletools',
        'turtle',
        'turtledemo',
        'webbrowser',
        'cgitb',
        'pydoc_data',
        'ensurepip',
        'venv',
        'lib2to3',
        'idlelib',
        'setuptools',
        'pkg_resources',
        'wheel',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='breathVOICE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/breathVOICE.ico' if os.path.exists('icon/breathVOICE.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='breathVOICE',
)
'''
    
    with open('breathVOICE.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建 breathVOICE.spec 文件")

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
        return True
    except ImportError:
        print("📦 正在安装 PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✅ PyInstaller 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller 安装失败")
            return False

def build_exe():
    """构建可执行文件"""
    print("🔨 开始构建 Windows 可执行文件...")
    
    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 已清理 build 目录")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 已清理 dist 目录")
    
    # 运行PyInstaller
    try:
        cmd = [
            'pyinstaller',
            '--clean',
            '--noconfirm',
            'breathVOICE.spec'
        ]
        
        print(f"🚀 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 构建成功！")
            print(f"📁 可执行文件位置: {os.path.abspath('dist/breathVOICE')}")
            return True
        else:
            print("❌ 构建失败:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ 找不到 pyinstaller 命令，请确保已正确安装")
        return False

def create_launcher_script():
    """创建启动脚本"""
    dist_dir = os.path.join(os.getcwd(), 'dist', 'breathVOICE')
    
    # 简化的中文启动脚本
    launcher_content = '''@echo off
title breathVOICE
echo Starting breathVOICE...
echo Please wait...
echo.
echo Browser will open at: http://127.0.0.1:7866
echo.
cd /d "%~dp0"
start http://127.0.0.1:7866
breathVOICE.exe
pause'''
    
    launcher_path = os.path.join(dist_dir, '启动 breathVOICE.bat')
    if os.path.exists(dist_dir):
        with open(launcher_path, 'w', encoding='gbk') as f:
            f.write(launcher_content)
        print(f"✓ 中文启动脚本已创建: {launcher_path}")
        
        # 简化的英文启动脚本
        launcher_content_en = '''@echo off
title breathVOICE
echo Starting breathVOICE...
echo Please wait...
echo.
echo Browser will open at: http://127.0.0.1:7866
echo.
cd /d "%~dp0"
start http://127.0.0.1:7866
breathVOICE.exe
pause'''
        
        launcher_path_en = os.path.join(dist_dir, 'Start breathVOICE.bat')
        with open(launcher_path_en, 'w', encoding='gbk') as f:
            f.write(launcher_content_en)
        print(f"✓ 英文启动脚本已创建: {launcher_path_en}")

def create_readme():
    """创建使用说明"""
    readme_content = '''# breathVOICE Windows 独立版

## 使用说明

1. 双击 "启动 breathVOICE.bat" 启动程序
2. 程序启动后会自动在浏览器中打开界面
3. 默认访问地址: http://localhost:7866

## 注意事项

- 首次启动可能需要较长时间，请耐心等待
- 确保系统防火墙允许程序访问网络
- 需要配置外部LLM API和TTS API才能正常使用所有功能

## 系统要求

- Windows 10 或更高版本
- 至少 4GB 可用内存
- 至少 2GB 可用磁盘空间

## 故障排除

如果程序无法启动，请检查：
1. 是否有杀毒软件阻止程序运行
2. 是否有其他程序占用7866端口
3. 系统是否有足够的内存和磁盘空间

## 技术支持

如有问题，请访问项目主页获取帮助：
https://github.com/LnbConceptions/breathVOICE
'''
    
    readme_path = 'dist/breathVOICE/使用说明.txt'
    if os.path.exists('dist/breathVOICE'):
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ 已创建使用说明: {readme_path}")

def main():
    """主函数"""
    print("🎯 breathVOICE Windows EXE 打包工具")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('app.py'):
        print("❌ 请在 breathVOICE 项目根目录下运行此脚本")
        return False
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return False
    
    # 创建规格文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_exe():
        return False
    
    # 创建辅助文件
    create_launcher_script()
    create_readme()
    
    print("\n🎉 打包完成！")
    print("📁 输出目录: dist/breathVOICE/")
    print("🚀 运行方式: 双击 '启动 breathVOICE.bat'")
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        input("\n按回车键退出...")
        sys.exit(1)
    else:
        input("\n按回车键退出...")