import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.mock_data_loader import (
    get_mock_pr_info,
    get_mock_pr_files,
    get_mock_diff,
    get_mock_llm_analysis,
    get_mock_review_response
)


class TestMockData:
    def test_load_mock_pr_info(self):
        pr_info = get_mock_pr_info()
        
        assert pr_info["number"] == 123
        assert pr_info["title"] == "feat: 添加用户认证功能"
        assert pr_info["user"]["login"] == "test-user"
        assert pr_info["additions"] == 200
        assert pr_info["deletions"] == 20
        assert pr_info["changed_files"] == 5

    def test_load_mock_pr_files(self):
        files = get_mock_pr_files()
        
        assert len(files) == 5
        assert files[0]["filename"] == "backend/auth/login.py"
        assert files[0]["status"] == "added"
        assert files[1]["filename"] == "backend/auth/jwt.py"
        assert files[2]["filename"] == "backend/models/user.py"
        assert files[3]["filename"] == "tests/test_auth.py"
        assert files[4]["filename"] == "backend/auth/register.py"

    def test_load_mock_diff(self):
        diff = get_mock_diff()
        
        assert "diff --git" in diff
        assert "backend/auth/login.py" in diff

    def test_load_mock_llm_analysis(self):
        analysis = get_mock_llm_analysis()
        
        assert "summary" in analysis
        assert "risks" in analysis
        assert len(analysis["risks"]) == 3
        assert analysis["risks"][0]["level"] == "high"
        assert analysis["risks"][0]["type"] == "security"

    def test_load_mock_review_response(self):
        response = get_mock_review_response()
        
        assert response["success"] is True
        assert response["data"]["pr_info"]["title"] == "feat: 添加用户认证功能"
        assert len(response["data"]["risks"]) == 2
        assert response["data"]["risks"][0]["level"] == "high"


class TestIntegration:
    def test_mock_data_integration(self):
        pr_info = get_mock_pr_info()
        files = get_mock_pr_files()
        diff = get_mock_diff()
        analysis = get_mock_llm_analysis()
        
        assert pr_info["changed_files"] == len(files)
        assert analysis["summary"] is not None
        assert len(analysis["risks"]) > 0
        
        for risk in analysis["risks"]:
            assert "level" in risk
            assert "file" in risk
            assert "description" in risk
            assert "suggestion" in risk


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
