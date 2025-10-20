@echo off
chcp 65001 >nul
title breathVOICE：个性化角色语音定制系统 - 启动器

echo.
echo ========================================
echo   breathVOICE：个性化角色语音定制系统
echo ========================================
echo.

:: 检查Python是否安装
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未检测到Python环境
    echo.
    echo 请先安装Python 3.8或更高版本：
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: 显示Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python环境检测成功：%PYTHON_VERSION%

:: 检查pip是否可用
echo.
echo [2/4] 检查pip包管理器...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：pip不可用
    echo 请确保pip已正确安装
    pause
    exit /b 1
)
echo ✅ pip可用

:: 检查requirements.txt是否存在
echo.
echo [3/4] 检查项目依赖...
if not exist "requirements.txt" (
    echo ❌ 错误：未找到requirements.txt文件
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

:: 检查关键依赖包是否已安装
echo 正在检查关键依赖包...
python -c "import gradio, torch, transformers, openai" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  检测到缺少依赖包，正在自动安装...
    echo.
    echo 安装依赖包（这可能需要几分钟时间）...
    pip install -r requirements.txt --no-warn-script-location
    
    :: 重新检查依赖包是否安装成功
    echo 验证依赖包安装状态...
    python -c "import gradio, torch, transformers, openai" >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ 依赖包安装失败
        echo 请检查网络连接或手动运行：pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
) else (
    echo ✅ 关键依赖包已安装
)

:: 检查app.py是否存在
echo.
echo [4/4] 启动breathVOICE系统...
if not exist "app.py" (
    echo ❌ 错误：未找到app.py文件
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

echo.
echo 🚀 正在启动breathVOICE系统...
echo 📍 访问地址：http://localhost:7866
echo 💡 启动完成后，请在浏览器中打开上述地址
echo.
echo ⚠️  注意：请保持此窗口打开，关闭窗口将停止服务
echo ========================================
echo.

:: 设置端口环境变量并启动应用
set GRADIO_SERVER_PORT=7866
python app.py

:: 如果程序异常退出，显示错误信息
if %errorlevel% neq 0 (
    echo.
    echo ❌ breathVOICE启动失败
    echo 错误代码：%errorlevel%
    echo.
    echo 💡 可能的解决方案：
    echo 1. 检查端口7866是否被其他程序占用
    echo 2. 重新运行此脚本以自动安装缺失的依赖包
    echo 3. 手动安装依赖：pip install -r requirements.txt
    echo 4. 检查Python版本是否为3.8或更高
    echo 5. 查看上方的详细错误信息进行排查
    echo.
    echo 📞 如需技术支持，请访问：https://github.com/LnbConceptions/breathVOICE
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b %errorlevel%
)

echo.
echo ✅ breathVOICE系统已成功启动！
echo 📍 访问地址：http://localhost:7866
echo.
echo ⚠️  注意：请保持此窗口打开，关闭窗口将停止服务
echo 💡 按Ctrl+C可以停止服务
echo.
echo 感谢使用breathVOICE系统！
echo.
:: 保持窗口打开，等待用户手动关闭
pause