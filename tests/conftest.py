#!/usr/bin/env python3
"""
pytestの設定ファイル

テスト用のフィクスチャを定義します。
"""

import json
import os
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def config_fixture():
    """テスト用の設定を提供する"""
    return {
        "github": {
            "repo_owner": "test-owner",
            "repo_name": "test-repo",
            "token_env_var": "GITHUB_TOKEN",
            "api_base_url": "https://api.github.com"
        },
        "data": {
            "storage_type": "file_per_pr",
            "pr_data_repo": "test-owner/pr-data",
            "base_dir": "prs",
            "indexes_dir": "indexes",
            "reports_dir": "reports"
        },
        "api": {
            "retry_count": 3,
            "rate_limit_wait": True,
            "request_delay": 0.1
        },
        "collectors": {
            "update_interval": 3600,
            "max_workers": 2
        }
    }


@pytest.fixture
def sample_pr_basic_info():
    """サンプルPRの基本情報"""
    return {
        "url": "https://api.github.com/repos/test-owner/test-repo/pulls/1",
        "id": 12345,
        "node_id": "PR_abcdef123456",
        "html_url": "https://github.com/test-owner/test-repo/pull/1",
        "number": 1,
        "state": "open",
        "title": "テスト用PR",
        "user": {
            "login": "test-user",
            "id": 1234567,
            "type": "User"
        },
        "body": "これはテスト用のPRです。\n\n## セクション1\n\nテスト内容です。",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "merged_at": None,
        "merge_commit_sha": None,
        "assignees": [],
        "requested_reviewers": [],
        "labels": [
            {
                "id": 123456,
                "name": "test-label",
                "color": "ff0000"
            }
        ],
        "draft": False
    }


@pytest.fixture
def sample_pr_comments():
    """サンプルPRのコメント"""
    return [
        {
            "id": 123456,
            "node_id": "comment_123456",
            "user": {
                "login": "test-user",
                "id": 1234567
            },
            "body": "テストコメントです。",
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-01T12:00:00Z"
        }
    ]


@pytest.fixture
def sample_pr_files():
    """サンプルPRのファイル変更"""
    return [
        {
            "sha": "abc123",
            "filename": "test.md",
            "status": "modified",
            "additions": 10,
            "deletions": 5,
            "changes": 15,
            "patch": "@@ -1,5 +1,10 @@\n # タイトル\n \n-## 古いセクション\n+## 新しいセクション\n \n テスト内容\n+\n+## 追加セクション\n+\n+新しい内容\n"
        }
    ]


@pytest.fixture
def sample_pr_labels():
    """サンプルPRのラベル"""
    return [
        {
            "id": 123456,
            "node_id": "label_123456",
            "url": "https://api.github.com/repos/test-owner/test-repo/labels/test-label",
            "name": "test-label",
            "color": "ff0000",
            "description": "テスト用ラベル"
        }
    ]


@pytest.fixture
def sample_pr_details(sample_pr_basic_info, sample_pr_comments, sample_pr_files, sample_pr_labels):
    """サンプルPRの詳細情報"""
    return {
        "basic_info": sample_pr_basic_info,
        "state": "open",
        "updated_at": "2023-01-02T00:00:00Z",
        "comments": sample_pr_comments,
        "review_comments": [],
        "commits": [
            {
                "sha": "abc123def456",
                "commit": {
                    "message": "テストコミット"
                },
                "author": {
                    "login": "test-user"
                }
            }
        ],
        "files": sample_pr_files,
        "labels": sample_pr_labels
    }


@pytest.fixture
def temp_data_dir(tmp_path):
    """一時的なデータディレクトリを作成"""
    data_dir = tmp_path / "prs"
    data_dir.mkdir()
    return data_dir
