from typing import Dict, List, Any
import time

from backend.services.github_service import GitHubService
from backend.services.llm_service import LLMService
from backend.models.schemas import RiskItem, ReviewData, PRInfo


class AnalyzerService:
    def __init__(self, github_token: str = None, llm_api_key: str = None):
        self.github_service = GitHubService(token=github_token)
        self.llm_service = LLMService(api_key=llm_api_key)

    def analyze_pr(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """分析PR并返回结果"""
        start_time = time.time()
        
        pr_info = self.github_service.get_pr_info(owner, repo, pr_number)
        files = self.github_service.get_pr_files(owner, repo, pr_number)
        diff = self.github_service.get_pr_diff(owner, repo, pr_number)
        
        analysis = self.llm_service.analyze_changes(pr_info, files, diff)
        
        processing_time = time.time() - start_time
        
        pr_info_formatted = PRInfo(
            title=pr_info.get("title", ""),
            author=pr_info.get("user", {}).get("login", ""),
            state=pr_info.get("state", ""),
            files_count=len(files),
            additions=pr_info.get("additions", 0),
            deletions=pr_info.get("deletions", 0)
        )
        
        risks = []
        for r in analysis.get("risks", []):
            risks.append(RiskItem(
                level=r.get("level", "medium"),
                file=r.get("file", ""),
                line=r.get("line", ""),
                type=r.get("type", "logic"),
                description=r.get("description", ""),
                suggestion=r.get("suggestion", "")
            ))
        
        review_data = ReviewData(
            pr_info=pr_info_formatted,
            summary=analysis.get("summary", ""),
            risks=risks,
            total_files=len(files),
            processing_time=round(processing_time, 2)
        )
        
        return {
            "success": True,
            "data": review_data.model_dump(),
            "error": None
        }

    @staticmethod
    def parse_risk_level(level_str: str) -> str:
        """解析风险等级"""
        level_str = level_str.lower()
        if level_str in ["high", "高", "h", "critical"]:
            return "high"
        elif level_str in ["medium", "中", "m", "warning"]:
            return "medium"
        elif level_str in ["low", "低", "l", "info"]:
            return "low"
        return "medium"

    @staticmethod
    def parse_risk_type(type_str: str) -> str:
        """解析风险类型"""
        type_str = type_str.lower()
        if type_str in ["security", "安全", "sec"]:
            return "security"
        elif type_str in ["logic", "逻辑", "log"]:
            return "logic"
        elif type_str in ["performance", "性能", "perf"]:
            return "performance"
        return "logic"

    @staticmethod
    def format_risk_output(risk: RiskItem) -> str:
        """格式化风险输出"""
        emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(risk.level, "⚪")
        
        return f"""{emoji} [{risk.level.upper()}] {risk.file}
类型: {risk.type}
位置: {risk.line or "N/A"}
描述: {risk.description}
建议: {risk.suggestion}"""
