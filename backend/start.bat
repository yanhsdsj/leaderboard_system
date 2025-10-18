@echo off
chcp 65001 >nul

echo [Backend] 启动中...

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 确认在 backend 目录
if not exist "requirements.txt" (
    echo 请在 backend 目录下运行此脚本。
    pause
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败。
    pause
    exit /b 1
)

echo 启动服务：http://localhost:8000
echo API 文档：http://localhost:8000/docs
echo 按 Ctrl+C 可停止服务。

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
