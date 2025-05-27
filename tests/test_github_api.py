#!/usr/bin/env python3
"""
GitHub API ユーティリティのテスト
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.utils.github_api import get_github_token, get_headers, make_github_api_request


@pytest.fixture
def mock_env_token():
    """環境変数のモック"""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}):
        yield


def test_get_github_token_from_env(mock_env_token):
    """環境変数からGitHubトークンを取得するテスト"""
    token = get_github_token()
    assert token == "test-token"


def test_get_headers_with_token(mock_env_token):
    """トークン付きヘッダーの取得テスト"""
    headers = get_headers()
    assert headers["Accept"] == "application/vnd.github.v3+json"
    assert headers["Authorization"] == "token test-token"


@patch("src.utils.github_api.requests.get")
def test_make_github_api_request(mock_get):
    """GitHub APIリクエストのテスト"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "value"}
    mock_get.return_value = mock_response
    
    result = make_github_api_request("https://api.github.com/test")
    
    assert result == {"key": "value"}
    mock_get.assert_called_once()
    assert mock_response.raise_for_status.called
