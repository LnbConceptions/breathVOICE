@echo off
chcp 65001 >nul
echo ========================================
echo breathVOICE Windows EXE 一键打包工具
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

:: 检查是否在正确的目录
if not exist "app.py" (
    echo ❌ 错误: 请在breathVOICE项目根目录下运行此脚本
    pause
    exit /b 1
)

echo ✅ 项目目录检查通过
echo.

:: 创建虚拟环境（可选）
echo 📦 正在准备构建环境...
if not exist "build_env" (
    echo 创建构建专用虚拟环境...
    python -m venv build_env
    if errorlevel 1 (
        echo ⚠️  虚拟环境创建失败，将使用系统Python环境
    ) else (
        echo ✅ 虚拟环境创建成功
    )
)

:: 激活虚拟环境
if exist "build_env\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call build_env\Scripts\activate.bat
)

:: 安装构建依赖
echo.
echo 📦 安装构建依赖...
pip install -r requirements_build.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败，尝试使用国内镜像源...
    pip install -r requirements_build.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

echo ✅ 依赖安装完成
echo.

:: 运行打包脚本
echo 🔨 开始打包...
python build_exe.py
if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

echo.
echo 🎉 打包完成！
echo 📁 可执行文件位置: dist\breathVOICE\
echo 🚀 运行方式: 双击 dist\breathVOICE\启动 breathVOICE.bat
echo.

:: 询问是否立即测试
set /p test_now="是否立即测试打包的程序？(y/n): "
if /i "%test_now%"=="y" (
    echo 正在启动测试...
    cd dist\breathVOICE
    start "" "启动 breathVOICE.bat"
    cd ..\..
)

echo.
echo 构建完成！按任意键退出...
pause >nul