from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routes import submit, leaderboard, health
from .services.storage_service import ensure_database_exists
from .services.backup_service import (
    ensure_backup_dirs, 
    backup_to_checkpoint,
    periodic_backup_task
)
import asyncio

# 创建FastAPI应用
app = FastAPI(
    title="Leaderboard Backend API",
    description="排行榜后端系统 - 学生作业提交与排名管理",
    version="1.0.0"
)

# 配置CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(submit.router)
app.include_router(leaderboard.router)
app.include_router(health.router)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    捕获所有未处理的异常，返回统一的错误格式
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "其他错误",
            "detail": str(exc)
        }
    )


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 确保数据库文件存在
    ensure_database_exists()
    print("✓ 数据库初始化完成")
    
    # 确保备份目录存在
    ensure_backup_dirs()
    print("✓ 备份目录初始化完成")
    
    # 启动时立即执行一次备份
    print("\n执行启动备份...")
    backup_to_checkpoint()
    print("✓ 启动备份完成\n")
    
    # 启动定期备份任务（每12小时）
    asyncio.create_task(periodic_backup_task())
    print("✓ 定期备份任务已启动（每12小时执行一次）")
    
    print("✓ 服务启动成功")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用Leaderboard Backend API",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

