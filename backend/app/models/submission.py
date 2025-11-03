from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Dict, Optional, Any, Literal
from datetime import datetime
from .student import StudentInfo


class Metrics(BaseModel):
    """
    评估指标模型 - 灵活支持任意指标字段
    
    每个作业可以有不同的metrics字段：
    - 作业1: MAE, MSE, RMSE, Prediction_Time
    - 作业2: Accuracy, Prediction_Time
    """
    model_config = ConfigDict(extra='allow')
    
    def model_dump(self, **kwargs):
        """覆盖model_dump方法，确保返回所有字段（包括额外字段）"""
        return super().model_dump(**kwargs)
    
    def __getitem__(self, key):
        """支持字典式访问"""
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        """支持字典式设置"""
        setattr(self, key, value)
    
    def get(self, key, default=None):
        """支持字典式get方法"""
        return getattr(self, key, default)
    
    def items(self):
        """支持字典式items方法"""
        return self.model_dump().items()
    
    def keys(self):
        """支持字典式keys方法"""
        return self.model_dump().keys()
    
    def values(self):
        """支持字典式values方法"""
        return self.model_dump().values()
    
    def dict(self, **kwargs):
        """兼容旧版Pydantic的dict方法"""
        return self.model_dump(**kwargs)


# 直接使用Dict类型，不需要单独的SubmittedFiles类
# 文件内容格式: Dict[filename, base64_content]
# 例如: {"solution.py": "base64编码", "model.py": "base64编码"}


class SubmissionRequest(BaseModel):
    """学生提交请求模型"""
    student_info: StudentInfo
    assignment_id: str = Field(..., description="作业编号")
    metrics: Metrics = Field(..., description="评估指标")
    checksums: Dict[str, str] = Field(..., description="文件MD5校验和")
    files: Optional[Dict[str, str]] = Field(None, description="提交的文件内容（可选），格式: {filename: base64_content}")
    main_contributor: Literal["human", "ai"] = Field(..., description="作业主要贡献者：human 或 ai")


class CompleteSubmissionData(BaseModel):
    """完整提交数据模型（后端内部使用）"""
    metrics: Metrics
    timestamp: str = Field(..., description="ISO格式时间戳")
    submission_count: int = Field(..., description="提交次数")
    checksums: Optional[Dict[str, str]] = Field(None, description="文件MD5校验和")
    files: Optional[Dict[str, str]] = Field(None, description="提交的文件内容，格式: {filename: base64_content}")
    main_contributor: str = Field(..., description="作业主要贡献者：human 或 ai")


class CompleteSubmission(BaseModel):
    """完整提交记录模型"""
    student_info: StudentInfo
    assignment_id: str
    submission_data: CompleteSubmissionData


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

