from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from backend.models.schemas import PRReviewRequest, PRReviewResponse, HealthResponse
from backend.services.analyzer_service import AnalyzerService
from backend.utils.url_parser import PRUrlParser
from backend.utils.exceptions import (
    InvalidPRUrlError, 
    GitHubAPIError, 
    PRNotFoundError, 
    RateLimitError,
    LLMError,
    TimeoutError as PRifyTimeoutError
)
from backend.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(status="ok")


@router.post("/review", response_model=PRReviewResponse)
async def review_pr(request: PRReviewRequest):
    """分析PR代码变更"""
    try:
        parsed = PRUrlParser.parse(request.pr_url)
        
        owner = parsed["owner"]
        repo = parsed["repo"]
        pr_number = parsed["pr_number"]
        
        analyzer = AnalyzerService(
            github_token=settings.github_token,
            llm_api_key=settings.deepseek_api_key
        )
        
        result = analyzer.analyze_pr(owner, repo, pr_number)
        
        return JSONResponse(content=result)
    
    except InvalidPRUrlError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "data": None,
                "error": f"无效的PR URL: {str(e)}"
            }
        )
    
    except PRNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "data": None,
                "error": f"PR不存在: {str(e)}"
            }
        )
    
    except RateLimitError as e:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "data": None,
                "error": f"API限流: {str(e)}"
            }
        )
    
    except PRifyTimeoutError as e:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "success": False,
                "data": None,
                "error": f"请求超时: {str(e)}"
            }
        )
    
    except LLMError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "error": f"LLM服务错误: {str(e)}"
            }
        )
    
    except GitHubAPIError as e:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "success": False,
                "data": None,
                "error": f"GitHub API错误: {str(e)}"
            }
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "error": f"未知错误: {str(e)}"
            }
        )
