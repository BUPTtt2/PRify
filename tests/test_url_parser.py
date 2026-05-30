import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.utils.url_parser import PRUrlParser
from backend.utils.exceptions import InvalidPRUrlError


class TestPRUrlParser:
    def test_parse_valid_url(self):
        url = "https://github.com/BUPTtt2/PRify/pull/1"
        result = PRUrlParser.parse(url)
        
        assert result["owner"] == "BUPTtt2"
        assert result["repo"] == "PRify"
        assert result["pr_number"] == 1
        assert "BUPTtt2" in result["url"]
    
    def test_parse_url_with_different_pr_number(self):
        url = "https://github.com/owner/repo/pull/123"
        result = PRUrlParser.parse(url)
        
        assert result["owner"] == "owner"
        assert result["repo"] == "repo"
        assert result["pr_number"] == 123
    
    def test_parse_url_with_extra_slashes(self):
        url = "https://github.com/my-org/my-repo/pull/456"
        result = PRUrlParser.parse(url)
        
        assert result["owner"] == "my-org"
        assert result["repo"] == "my-repo"
        assert result["pr_number"] == 456
    
    def test_parse_empty_url(self):
        with pytest.raises(InvalidPRUrlError, match="URL不能为空"):
            PRUrlParser.parse("")
    
    def test_parse_whitespace_url(self):
        with pytest.raises(InvalidPRUrlError, match="URL不能为空"):
            PRUrlParser.parse("   ")
    
    def test_parse_invalid_github_url(self):
        with pytest.raises(InvalidPRUrlError, match="必须是GitHub仓库URL"):
            PRUrlParser.parse("https://gitlab.com/owner/repo/pull/1")
    
    def test_parse_invalid_url_no_pull(self):
        with pytest.raises(InvalidPRUrlError, match="URL必须包含/pull/路径"):
            PRUrlParser.parse("https://github.com/owner/repo/issues/1")
    
    def test_parse_invalid_pr_number(self):
        with pytest.raises(InvalidPRUrlError, match="PR编号必须是数字"):
            PRUrlParser.parse("https://github.com/owner/repo/pull/abc")
    
    def test_parse_invalid_pr_number_zero(self):
        with pytest.raises(InvalidPRUrlError, match="PR编号必须是正整数"):
            PRUrlParser.parse("https://github.com/owner/repo/pull/0")
    
    def test_parse_invalid_pr_number_negative(self):
        with pytest.raises(InvalidPRUrlError, match="PR编号必须是正整数"):
            PRUrlParser.parse("https://github.com/owner/repo/pull/-1")
    
    def test_parse_incomplete_url(self):
        with pytest.raises(InvalidPRUrlError, match="URL格式不正确"):
            PRUrlParser.parse("https://github.com/owner")
    
    def test_validate_valid_url(self):
        url = "https://github.com/owner/repo/pull/1"
        is_valid, error = PRUrlParser.validate(url)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_url(self):
        url = "invalid-url"
        is_valid, error = PRUrlParser.validate(url)
        
        assert is_valid is False
        assert error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
