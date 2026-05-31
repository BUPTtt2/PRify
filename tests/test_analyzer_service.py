import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.analyzer_service import AnalyzerService
from backend.models.schemas import RiskItem


class TestAnalyzerService:
    def test_analyze_pr(self):
        mock_pr_info = {
            "title": "Test PR",
            "user": {"login": "test-user"},
            "state": "open",
            "additions": 100,
            "deletions": 50
        }
        
        mock_files = [
            {"filename": "test.py", "status": "modified", "additions": 50, "deletions": 20}
        ]
        
        mock_diff = "diff content"
        
        mock_analysis = {
            "summary": "测试变更总结",
            "risks": [
                {
                    "level": "high",
                    "file": "test.py",
                    "line": "10-15",
                    "type": "security",
                    "description": "发现硬编码密钥",
                    "suggestion": "使用环境变量"
                }
            ]
        }
        
        with patch.object(AnalyzerService, '__init__', lambda self, *args, **kwargs: None):
            analyzer = AnalyzerService()
            analyzer.github_service = Mock()
            analyzer.llm_service = Mock()
            
            analyzer.github_service.get_pr_info.return_value = mock_pr_info
            analyzer.github_service.get_pr_files.return_value = mock_files
            analyzer.github_service.get_pr_diff.return_value = mock_diff
            analyzer.llm_service.analyze_changes.return_value = mock_analysis
            
            result = analyzer.analyze_pr("owner", "repo", 1)
            
            assert result["success"] is True
            assert result["data"]["pr_info"]["title"] == "Test PR"
            assert result["data"]["pr_info"]["author"] == "test-user"
            assert len(result["data"]["risks"]) == 1
            assert result["data"]["risks"][0]["level"] == "high"

    def test_parse_risk_level(self):
        assert AnalyzerService.parse_risk_level("high") == "high"
        assert AnalyzerService.parse_risk_level("HIGH") == "high"
        assert AnalyzerService.parse_risk_level("高") == "high"
        assert AnalyzerService.parse_risk_level("medium") == "medium"
        assert AnalyzerService.parse_risk_level("low") == "low"
        assert AnalyzerService.parse_risk_level("unknown") == "medium"

    def test_parse_risk_type(self):
        assert AnalyzerService.parse_risk_type("security") == "security"
        assert AnalyzerService.parse_risk_type("SECURITY") == "security"
        assert AnalyzerService.parse_risk_type("logic") == "logic"
        assert AnalyzerService.parse_risk_type("performance") == "performance"
        assert AnalyzerService.parse_risk_type("unknown") == "logic"

    def test_format_risk_output(self):
        risk = RiskItem(
            level="high",
            file="test.py",
            line="10-15",
            type="security",
            description="发现硬编码密钥",
            suggestion="使用环境变量"
        )
        
        output = AnalyzerService.format_risk_output(risk)
        
        assert "🔴" in output
        assert "HIGH" in output
        assert "test.py" in output
        assert "security" in output
        assert "发现硬编码密钥" in output
        assert "使用环境变量" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
