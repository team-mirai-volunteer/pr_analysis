#!/usr/bin/env python3
"""
PRコレクターのテスト
"""

import json
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from src.collectors.pr_collector import PRCollector


def test_init_with_config(config_fixture):
    """設定を指定して初期化するテスト"""
    collector = PRCollector(config_fixture)
    assert collector.repo_owner == "test-owner"
    assert collector.repo_name == "test-repo"
    assert collector.api_base_url == "https://api.github.com"


@patch("src.collectors.pr_collector.make_github_api_request")
def test_get_pull_requests(mock_api_request, config_fixture):
    """Pull Requestの取得テスト"""
    mock_api_request.return_value = [
        {"number": 1, "title": "Test PR 1"},
        {"number": 2, "title": "Test PR 2"}
    ]
    
    collector = PRCollector(config_fixture)
    prs = collector.get_pull_requests(limit=2)
    
    assert len(prs) == 2
    assert prs[0]["number"] == 1
    assert prs[1]["number"] == 2
    mock_api_request.assert_called_once()


@patch("src.collectors.pr_collector.make_github_api_request")
def test_get_pr_details(mock_api_request, config_fixture, sample_pr_basic_info, sample_pr_comments, sample_pr_labels):
    """PR詳細情報の取得テスト"""
    mock_api_request.side_effect = [
        sample_pr_basic_info,  # get_pr_by_number
        sample_pr_labels,      # get_pr_labels
        sample_pr_comments,    # get_pr_comments
        [],                    # get_pr_review_comments
        [{"sha": "abc123"}],   # get_pr_commits
        [{"filename": "test.md"}]  # get_pr_files
    ]
    
    collector = PRCollector(config_fixture)
    pr_details = collector.get_pr_details(1)
    
    assert pr_details["basic_info"] == sample_pr_basic_info
    assert pr_details["labels"] == sample_pr_labels
    assert pr_details["comments"] == sample_pr_comments
    assert len(pr_details["commits"]) == 1
    assert len(pr_details["files"]) == 1
    assert mock_api_request.call_count == 6


def test_save_pr_to_file(config_fixture, sample_pr_details, temp_data_dir):
    """PRデータをファイルに保存するテスト"""
    collector = PRCollector(config_fixture)
    
    result = collector.save_pr_to_file(sample_pr_details, output_dir=temp_data_dir)
    
    assert result is True
    pr_file = temp_data_dir / "1.json"
    assert pr_file.exists()
    
    with open(pr_file, encoding="utf-8") as f:
        saved_data = json.load(f)
    
    assert saved_data["basic_info"]["number"] == 1
    assert saved_data["basic_info"]["title"] == "テスト用PR"
    assert "labels" in saved_data
    assert len(saved_data["labels"]) == 1
