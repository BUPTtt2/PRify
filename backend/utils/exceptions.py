class PRifyError(Exception):
    """基础异常类"""
    pass


class InvalidPRUrlError(PRifyError):
    """无效的PR URL"""
    pass


class GitHubAPIError(PRifyError):
    """GitHub API错误"""
    pass


class PRNotFoundError(GitHubAPIError):
    """PR不存在"""
    pass


class RateLimitError(GitHubAPIError):
    """API限流"""
    pass


class LLMError(PRifyError):
    """LLM调用错误"""
    pass


class TimeoutError(PRifyError):
    """超时错误"""
    pass
