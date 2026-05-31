from typing import Optional
from .exceptions import InvalidPRUrlError


class PRUrlParser:
    GITHUB_PR_URL_PATTERN = "https://github.com/{owner}/{repo}/pull/{pr_number}"
    
    @staticmethod
    def parse(url: str) -> dict:
        """
        解析GitHub PR URL
        
        Args:
            url: GitHub PR URL, e.g., https://github.com/owner/repo/pull/123
            
        Returns:
            dict: 包含 owner, repo, pr_number
            
        Raises:
            InvalidPRUrlError: URL格式无效时
        """
        url = url.strip() if url else ""
        
        if not url:
            raise InvalidPRUrlError("URL不能为空")
        
        if not url.startswith("https://github.com/"):
            raise InvalidPRUrlError("必须是GitHub仓库URL，格式：https://github.com/owner/repo/pull/123")
        
        parts = url.replace("https://github.com/", "").split("/")
        
        if len(parts) < 4:
            raise InvalidPRUrlError("URL格式不正确，应为：https://github.com/owner/repo/pull/123")
        
        if parts[2] != "pull":
            raise InvalidPRUrlError("URL必须包含/pull/路径")
        
        owner = parts[0]
        repo = parts[1]
        
        try:
            pr_number = int(parts[3])
        except (ValueError, IndexError):
            raise InvalidPRUrlError("PR编号必须是数字")
        
        if pr_number <= 0:
            raise InvalidPRUrlError("PR编号必须是正整数")
        
        return {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number,
            "url": PRUrlParser.GITHUB_PR_URL_PATTERN.format(
                owner=owner,
                repo=repo,
                pr_number=pr_number
            )
        }
    
    @staticmethod
    def validate(url: str) -> tuple[bool, Optional[str]]:
        """
        验证URL是否有效
        
        Args:
            url: GitHub PR URL
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        try:
            PRUrlParser.parse(url)
            return True, None
        except InvalidPRUrlError as e:
            return False, str(e)
