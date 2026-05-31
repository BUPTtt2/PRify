from fastapi import APIRouter, HTTPException
from ..models.schemas import PRReviewRequest, PRReviewResponse
from ..services.analyzer_service import AnalyzerService
from ..utils.exceptions import (
    PRifyError,
    InvalidPRUrlError,
    GitHubAPIError,
    RateLimitError,
    LLMError
)

router = APIRouter(prefix="/api", tags=["review"])


@router.post("/review", response_model=PRReviewResponse)
async def review_pr(request: PRReviewRequest):
    try:
        analyzer = AnalyzerService()
        result = analyzer.analyze_pr(request.pr_url)
        return PRReviewResponse(**result)
    except InvalidPRUrlError as e:
        return PRReviewResponse(
            success=False,
            error=f"无效的PR URL: {str(e)}"
        )
    except GitHubAPIError as e:
        return PRReviewResponse(
            success=False,
            error=f"GitHub API错误: {str(e)}"
        )
    except RateLimitError as e:
        return PRReviewResponse(
            success=False,
            error=f"API限流: {str(e)}"
        )
    except LLMError as e:
        return PRReviewResponse(
            success=False,
            error=f"LLM分析错误: {str(e)}"
        )
    except Exception as e:
        return PRReviewResponse(
            success=False,
            error=f"未知错误: {str(e)}"
        )
