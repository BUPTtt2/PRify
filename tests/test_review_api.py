import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.main import app
from backend.utils.exceptions import InvalidPRUrlError, PRNotFoundError, RateLimitError


client = TestClient(app)


class TestReviewAPI:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_review_pr_invalid_url(self):
        response = client.post("/api/review", json={"pr_url": "invalid-url"})
        
        assert response.status_code == 400
        assert response.json()["success"] is False
        assert "无效的PR URL" in response.json()["error"]

    def test_review_pr_empty_url(self):
        response = client.post("/api/review", json={"pr_url": ""})
        
        assert response.status_code == 400
        assert response.json()["success"] is False

    def test_review_pr_not_found(self):
        with patch('backend.routers.review.AnalyzerService') as mock_analyzer:
            mock_analyzer.return_value.analyze_pr.side_effect = PRNotFoundError("PR不存在")
            
            response = client.post(
                "/api/review", 
                json={"pr_url": "https://github.com/owner/repo/pull/1"}
            )
            
            assert response.status_code == 404
            assert response.json()["success"] is False
            assert "PR不存在" in response.json()["error"]

    def test_review_pr_rate_limit(self):
        with patch('backend.routers.review.AnalyzerService') as mock_analyzer:
            mock_analyzer.return_value.analyze_pr.side_effect = RateLimitError("API限流")
            
            response = client.post(
                "/api/review", 
                json={"pr_url": "https://github.com/owner/repo/pull/1"}
            )
            
            assert response.status_code == 429
            assert response.json()["success"] is False
            assert "限流" in response.json()["error"]

    def test_review_pr_success(self):
        mock_result = {
            "success": True,
            "data": {
                "pr_info": {
                    "title": "Test PR",
                    "author": "test-user",
                    "state": "open",
                    "files_count": 5,
                    "additions": 100,
                    "deletions": 50
                },
                "summary": "测试变更",
                "risks": [],
                "total_files": 5,
                "processing_time": 1.5
            },
            "error": None
        }
        
        with patch('backend.routers.review.AnalyzerService') as mock_analyzer:
            mock_analyzer.return_value.analyze_pr.return_value = mock_result
            
            response = client.post(
                "/api/review", 
                json={"pr_url": "https://github.com/owner/repo/pull/1"}
            )
            
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert response.json()["data"]["pr_info"]["title"] == "Test PR"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
