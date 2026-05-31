import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

from backend.config import settings
from backend.utils.exceptions import GitHubAPIError, PRNotFoundError, RateLimitError


class GitHubService:
    BASE_URL = "https://api.github.com/"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.github_token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PRify-AI-PR-Review"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def _fetch(self, endpoint: str, method: str = "GET", return_text: bool = False, **kwargs) -> Any:
        """封装HTTP请求"""
        url = urljoin(self.BASE_URL, endpoint)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=settings.github_timeout,
                **kwargs
            )
            
            if response.status_code == 404:
                raise PRNotFoundError("PR不存在或无权访问")
            
            if response.status_code == 403:
                remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
                if remaining == 0:
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    raise RateLimitError(f"API限流，剩余请求数为0，预计重置时间: {reset_time}")
            
            response.raise_for_status()
            
            if return_text:
                return response.text
            return response.json()
        
        except requests.exceptions.Timeout:
            raise GitHubAPIError("请求超时")
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"网络请求失败: {str(e)}")
    
    def _fetch_raw(self, url: str) -> str:
        """获取原始文本内容"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=settings.github_timeout
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            raise GitHubAPIError("请求超时")
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"网络请求失败: {str(e)}")
    
    def get_pr_info(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """获取PR基本信息"""
        endpoint = f"repos/{owner}/{repo}/pulls/{pr_number}"
        return self._fetch(endpoint)
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """获取PR变更文件列表"""
        endpoint = f"repos/{owner}/{repo}/pulls/{pr_number}/files"
        return self._fetch(endpoint)
    
    def get_file_diff(self, owner: str, repo: str, pr_number: int, filename: str) -> str:
        """获取单个文件的diff"""
        endpoint = f"repos/{owner}/{repo}/pulls/{pr_number}"
        pr_data = self._fetch(endpoint)
        
        if "diff_url" in pr_data:
            diff_content = self._fetch_raw(pr_data["diff_url"])
            
            lines = diff_content.split("\n")
            file_diff = []
            in_file = False
            file_header = f"diff --git a/{filename} b/{filename}"
            
            for line in lines:
                if line.startswith("diff --git"):
                    if in_file:
                        break
                    if line == file_header or (filename in line):
                        in_file = True
                        file_diff.append(line)
                elif in_file:
                    file_diff.append(line)
            
            return "\n".join(file_diff)
        
        return ""
    
    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """获取完整的PR diff"""
        endpoint = f"repos/{owner}/{repo}/pulls/{pr_number}"
        pr_data = self._fetch(endpoint)
        
        if "diff_url" in pr_data:
            return self._fetch_raw(pr_data["diff_url"])
        
        return ""
    
    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库信息"""
        endpoint = f"repos/{owner}/{repo}"
        return self._fetch(endpoint)
    
    def get_rate_limit(self) -> Dict[str, Any]:
        """获取API限流状态"""
        try:
            response = requests.get(
                urljoin(self.BASE_URL, "rate_limit"),
                headers=self.headers,
                timeout=settings.github_timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise GitHubAPIError(f"获取限流状态失败: {str(e)}")


def fetch_with_retry(service: GitHubService, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
    """获取PR信息和文件列表"""
    pr_info = service.get_pr_info(owner, repo, pr_number)
    files = service.get_pr_files(owner, repo, pr_number)
    
    return {
        "pr_info": pr_info,
        "files": files
    }
