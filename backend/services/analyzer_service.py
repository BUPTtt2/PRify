from typing import Dict, Any, List
from .github_service import GitHubService
from .llm_service import LLMService
from ..config import settings
from ..models.schemas import PRInfo, RiskItem, ReviewData
from ..utils.url_parser import PRUrlParser


class AnalyzerService:
    def __init__(self, github_token: str = None, llm_api_key: str = None):
        self.github_service = GitHubService(github_token or settings.github_token)
        self.llm_service = LLMService(api_key=llm_api_key or settings.deepseek_api_key)

    def analyze_pr(self, pr_url: str) -> Dict[str, Any]:
        parsed = PRUrlParser.parse(pr_url)
        owner = parsed["owner"]
        repo = parsed["repo"]
        pr_number = parsed["pr_number"]

        pr_info = self.github_service.get_pr_info(owner, repo, pr_number)
        files = self.github_service.get_pr_files(owner, repo, pr_number)
        diff = self.github_service.get_pr_diff(owner, repo, pr_number)

        analysis = self.llm_service.analyze_changes(pr_info, files, diff)

        return {
            "success": True,
            "data": {
                "pr_info": PRInfo(**pr_info),
                "summary": analysis.get("summary", ""),
                "risks": [RiskItem(**risk) for risk in analysis.get("risks", [])],
                "positive_points": analysis.get("positive_points", [])
            }
        }
