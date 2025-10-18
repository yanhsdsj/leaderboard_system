@echo off
chcp 65001 >nul

echo [Frontend] 启动中...

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到 Node.js，请先安装：https://nodejs.org/
    pause
    exit /b 1
)

REM 确认在 frontend 目录
if not exist "package.json" (
    echo 请在 frontend 目录下运行此脚本。
    pause
    exit /b 1
)

REM 安装依赖（如未安装）
if not exist "node_modules" (
    echo 正在安装依赖...
    npm install
    if errorlevel 1 (
        echo 依赖安装失败。
        pause
        exit /b 1
    )
)

echo 启动开发服务器：http://localhost:3000
echo 后端服务：http://localhost:8000
echo 按 Ctrl+C 可停止服务。

npm run dev
