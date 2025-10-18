from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime
from .student import StudentInfo


class Metrics(BaseModel):
    """评估指标模型"""
    MAE: float = Field(..., description="平均绝对误差")
    MSE: float = Field(..., description="均方误差")
    RMSE: float = Field(..., description="均方根误差")
    Prediction_Time: float = Field(..., description="预测时间")


class SubmissionData(BaseModel):
    """提交数据模型（用户提交时）"""
    metrics: Metrics


class CompleteSubmissionData(BaseModel):
    """完整提交数据模型（后端补充）"""
    metrics: Metrics
    timestamp: str = Field(..., description="ISO格式时间戳")
    submission_count: int = Field(..., description="提交次数")


class SubmissionRequest(BaseModel):
    """学生提交请求模型"""
    student_info: StudentInfo
    assignment_id: str = Field(..., description="作业编号")
    submission_data: SubmissionData
    signature: Optional[str] = Field(None, description="客户端签名（可选）")


class CompleteSubmission(BaseModel):
    """完整提交记录模型（包含签名）"""
    student_info: StudentInfo
    assignment_id: str
    submission_data: CompleteSubmissionData
    signature: str = Field(..., description="HMAC-SHA256签名")


class SubmissionResponse(BaseModel):
    """提交响应模型"""
    success: bool
    message: str
    submission_count: int
    leaderboard_updated: bool
    current_rank: Optional[int] = None
    score: Optional[float] = None
    previous_score: Optional[float] = None


class LeaderboardEntry(BaseModel):
    """排行榜条目模型"""
    rank: int
    student_info: StudentInfo
    score: float
    metrics: Metrics
    timestamp: str
    submission_count: int

