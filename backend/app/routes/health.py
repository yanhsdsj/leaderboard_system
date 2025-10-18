from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """
    健康检查接口
    
    Returns:
        服务状态信息
    """
    return {
        "status": "healthy",
        "service": "Leaderboard Backend",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }

