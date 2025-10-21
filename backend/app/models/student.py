from pydantic import BaseModel, Field
from typing import Optional


class StudentInfo(BaseModel):
    """学生信息模型"""
    student_id: str = Field(..., description="学生唯一ID")
    name: str = Field(..., description="学生姓名")
    nickname: Optional[str] = Field(None, description="学生昵称")

