@echo off
echo 🚀 安装 Claude Code 剪切板监听器...

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 需要 Python 3
    pause
    exit /b 1
)

REM 安装依赖
echo 📦 安装依赖...
pip install pillow pyperclip psutil

REM 创建启动脚本
echo @echo off > start_clipboard_monitor.bat
echo cd /d "%%~dp0" >> start_clipboard_monitor.bat
echo python clipboard_monitor.py >> start_clipboard_monitor.bat
echo pause >> start_clipboard_monitor.bat

echo ✅ 安装完成！
echo.
echo 使用方法:
echo   start_clipboard_monitor.bat     # 启动监听器
echo   python clipboard_monitor.py     # 直接运行
echo.
echo 功能:
echo   📋 监听剪切板图片
echo   💾 自动保存到 .tmp/ 目录  
echo   🔄 替换为文件路径引用
echo   🧹 自动清理过期文件
pause