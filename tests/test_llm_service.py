import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.llm_service import LLMService
from backend.utils.exceptions import LLMError, TimeoutError


class TestLLMService:
    def test_init_with_api_key(self):
        service = LLMService(api_key="test-key")
        assert service.api_key == "test-key"

    def test_build_headers(self):
        service = LLMService(api_key="test-key")
        headers = service._build_headers()
        
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-key"

    def test_build_payload(self):
        service = LLMService(api_key="test-key")
        messages = [{"role": "user", "content": "hello"}]
        payload = service._build_payload(messages)
        
        assert payload["model"] == "deepseek-chat"
        assert payload["messages"] == messages
        assert payload["max_tokens"] == 2000
        assert payload["temperature"] == 0.3

    def test_call_llm_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "分析完成"}}]
        }
        mock_response.raise_for_status = Mock()
        
        with patch('backend.services.llm_service.requests.post') as mock_post:
            mock_post.return_value = mock_response
            
            service = LLMService(api_key="test-key")
            result = service.call_llm("请分析这段代码")
            
            assert result == "分析完成"
            mock_post.assert_called_once()

    def test_call_llm_timeout(self):
        import requests
        with patch('backend.services.llm_service.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout()
            
            service = LLMService(api_key="test-key")
            
            with pytest.raises(TimeoutError):
                service.call_llm("test prompt")

    def test_call_llm_api_error(self):
        import requests
        with patch('backend.services.llm_service.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("API Error")
            
            service = LLMService(api_key="test-key")
            
            with pytest.raises(LLMError, match="LLM API调用失败"):
                service.call_llm("test prompt")

    def test_call_llm_invalid_response(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "response"}
        mock_response.raise_for_status = Mock()
        
        with patch('backend.services.llm_service.requests.post') as mock_post:
            mock_post.return_value = mock_response
            
            service = LLMService(api_key="test-key")
            
            with pytest.raises(LLMError, match="LLM响应格式错误"):
                service.call_llm("test prompt")

    def test_summarize_files(self):
        service = LLMService(api_key="test-key")
        files = [
            {"filename": "test.py", "status": "modified", "additions": 10, "deletions": 5},
            {"filename": "new.py", "status": "added", "additions": 20, "deletions": 0}
        ]
        
        summary = service._summarize_files(files)
        
        assert "test.py" in summary
        assert "new.py" in summary
        assert "+10" in summary
        assert "+20" in summary

    def test_parse_analysis_response_valid_json(self):
        service = LLMService(api_key="test-key")
        response = '''```json
        {
            "summary": "变更总结",
            "risks": [
                {
                    "level": "high",
                    "file": "test.py",
                    "type": "security",
                    "description": "发现风险",
                    "suggestion": "修复建议"
                }
            ]
        }
        ```'''
        
        result = service._parse_analysis_response(response)
        
        assert result["summary"] == "变更总结"
        assert len(result["risks"]) == 1
        assert result["risks"][0]["level"] == "high"

    def test_parse_analysis_response_invalid_json(self):
        service = LLMService(api_key="test-key")
        response = "这是一段普通文本回复，不是JSON格式"
        
        result = service._parse_analysis_response(response)
        
        assert "summary" in result
        assert result["parse_error"] is True

    def test_analyze_changes(self):
        mock_response = '''```json
        {
            "summary": "添加用户认证功能",
            "risks": [
                {
                    "level": "high",
                    "file": "auth.py",
                    "line": "25-30",
                    "type": "security",
                    "description": "硬编码密钥",
                    "suggestion": "使用环境变量"
                }
            ]
        }
        ```'''
        
        mock_llm = Mock(return_value=mock_response)
        
        with patch.object(LLMService, 'call_llm', mock_llm):
            service = LLMService(api_key="test-key")
            
            pr_info = {
                "title": "Add auth",
                "user": {"login": "test"},
                "additions": 100,
                "deletions": 50
            }
            files = [
                {"filename": "auth.py", "status": "added", "additions": 50, "deletions": 0}
            ]
            diffs = "diff content"
            
            result = service.analyze_changes(pr_info, files, diffs)
            
            assert result["summary"] == "添加用户认证功能"
            assert len(result["risks"]) == 1
            assert result["risks"][0]["level"] == "high"

    def test_generate_summary(self):
        mock_llm = Mock(return_value="变更主要是添加新功能")
        
        with patch.object(LLMService, 'call_llm', mock_llm):
            service = LLMService(api_key="test-key")
            
            pr_info = {"title": "Add feature", "user": {"login": "test"}}
            files = [{"filename": "test.py"}]
            
            result = service.generate_summary(pr_info, files)
            
            assert result == "变更主要是添加新功能"

    def test_identify_risks(self):
        mock_response = '''[
            {"level": "high", "description": "发现硬编码密钥", "type": "security"},
            {"level": "medium", "description": "缺少边界检查", "type": "logic"}
        ]'''
        
        mock_llm = Mock(return_value=mock_response)
        
        with patch.object(LLMService, 'call_llm', mock_llm):
            service = LLMService(api_key="test-key")
            
            result = service.identify_risks("some diff content")
            
            assert len(result) == 2
            assert result[0]["level"] == "high"
            assert result[1]["type"] == "logic"

    def test_generate_suggestions(self):
        mock_response = '''[
            "建议1: 使用环境变量",
            "建议2: 添加边界检查"
        ]'''
        
        mock_llm = Mock(return_value=mock_response)
        
        with patch.object(LLMService, 'call_llm', mock_llm):
            service = LLMService(api_key="test-key")
            
            risks = [
                {"level": "high", "description": "风险1"},
                {"level": "medium", "description": "风险2"}
            ]
            
            result = service.generate_suggestions(risks)
            
            assert len(result) == 2
            assert "环境变量" in result[0]

    def test_generate_suggestions_empty_risks(self):
        service = LLMService(api_key="test-key")
        
        result = service.generate_suggestions([])
        
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
