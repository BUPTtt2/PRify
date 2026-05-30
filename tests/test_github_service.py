import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.github_service import GitHubService
from backend.utils.exceptions import GitHubAPIError, PRNotFoundError, RateLimitError


class TestGitHubService:
    def test_init_with_token(self):
        service = GitHubService(token="test-token")
        assert service.token == "test-token"
        assert service.headers["Authorization"] == "token test-token"
    
    def test_init_without_token(self):
        service = GitHubService()
        assert service.token is not None
        assert "Authorization" not in service.headers or service.headers["Authorization"] == "token "
    
    def test_get_pr_info_success(self):
        mock_response = {
            "number": 1,
            "title": "Test PR",
            "user": {"login": "test-user"},
            "state": "open",
            "additions": 10,
            "deletions": 5,
            "changed_files": 2
        }
        
        with patch.object(GitHubService, '_fetch') as mock_fetch:
            mock_fetch.return_value = mock_response
            
            service = GitHubService(token="test-token")
            result = service.get_pr_info("owner", "repo", 1)
            
            assert result["number"] == 1
            assert result["title"] == "Test PR"
            assert result["user"]["login"] == "test-user"
            mock_fetch.assert_called_once_with("repos/owner/repo/pulls/1")
    
    def test_get_pr_info_not_found(self):
        with patch.object(GitHubService, '_fetch') as mock_fetch:
            mock_fetch.side_effect = PRNotFoundError("PR不存在")
            
            service = GitHubService(token="test-token")
            
            with pytest.raises(PRNotFoundError):
                service.get_pr_info("owner", "repo", 999)
    
    def test_get_pr_info_rate_limit(self):
        with patch.object(GitHubService, '_fetch') as mock_fetch:
            mock_fetch.side_effect = RateLimitError("API限流")
            
            service = GitHubService(token="test-token")
            
            with pytest.raises(RateLimitError):
                service.get_pr_info("owner", "repo", 1)
    
    def test_get_pr_files(self):
        mock_files = [
            {"filename": "test.py", "additions": 5, "deletions": 2, "status": "modified"},
            {"filename": "test2.py", "additions": 10, "deletions": 0, "status": "added"}
        ]
        
        with patch.object(GitHubService, '_fetch') as mock_fetch:
            mock_fetch.return_value = mock_files
            
            service = GitHubService(token="test-token")
            result = service.get_pr_files("owner", "repo", 1)
            
            assert len(result) == 2
            assert result[0]["filename"] == "test.py"
            assert result[1]["filename"] == "test2.py"
    
    def test_get_pr_diff(self):
        mock_pr_data = {
            "diff_url": "https://github.com/owner/repo/pull/1.diff"
        }
        
        mock_diff = """diff --git a/test.py b/test.py
index abc123..def456 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
def hello():
-    print("Hello")
+    print("Hello World")
"""
        
        with patch.object(GitHubService, '_fetch') as mock_fetch, \
             patch.object(GitHubService, '_fetch_raw') as mock_fetch_raw:
            mock_fetch.return_value = mock_pr_data
            mock_fetch_raw.return_value = mock_diff
            
            service = GitHubService(token="test-token")
            result = service.get_pr_diff("owner", "repo", 1)
            
            assert "diff --git" in result
            assert "Hello World" in result
            mock_fetch_raw.assert_called_once_with("https://github.com/owner/repo/pull/1.diff")
    
    def test_get_file_diff(self):
        mock_pr_data = {
            "diff_url": "https://github.com/owner/repo/pull/1.diff"
        }
        
        mock_diff = """diff --git a/test.py b/test.py
index abc123..def456 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
def hello():
-    print("Hello")
+    print("Hello World")

diff --git a/other.py b/other.py
index 123abc..456def 100644
--- a/other.py
+++ b/other.py
@@ -1 +1 @@
-print("other")
+print("changed")
"""
        
        with patch.object(GitHubService, '_fetch') as mock_fetch, \
             patch.object(GitHubService, '_fetch_raw') as mock_fetch_raw:
            mock_fetch.return_value = mock_pr_data
            mock_fetch_raw.return_value = mock_diff
            
            service = GitHubService(token="test-token")
            result = service.get_file_diff("owner", "repo", 1, "test.py")
            
            assert "test.py" in result
            assert "Hello World" in result
            assert "other.py" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
