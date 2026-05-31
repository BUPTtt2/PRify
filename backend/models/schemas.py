from pydantic import BaseModel, Field
from typing import Optional, List


class PRReviewRequest(BaseModel):
    pr_url: str = Field(..., description="GitHub PR URL")


class PRInfo(BaseModel):
    title: str
    author: str
    state: str
    files_count: int
    additions: int
    deletions: int


class RiskItem(BaseModel):
    level: str = Field(..., description="风险等级：high/medium/low")
    file: str = Field(..., description="风险所在文件")
    line: Optional[str] = Field(None, description="风险所在行号或范围")
    type: str = Field(..., description="风险类型：security/logic/performance")
    description: str = Field(..., description="风险描述")
    suggestion: str = Field(..., description="改进建议")


class ReviewData(BaseModel):
    pr_info: PRInfo
    summary: str
    risks: List[RiskItem]
    total_files: int
    processing_time: float


class PRReviewResponse(BaseModel):
    success: bool
    data: Optional[ReviewData] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
