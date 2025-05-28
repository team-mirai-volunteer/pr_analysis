#!/usr/bin/env python3
"""
ラベルレポート生成器のテスト
"""

import json
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from src.generators.label_report import LabelReportGenerator


def test_init_with_config(config_fixture):
    """設定を指定して初期化するテスト"""
    generator = LabelReportGenerator(config_fixture)
    assert generator.config == config_fixture


def test_group_prs_by_label(sample_pr_details):
    """PRをラベルごとにグループ化するテスト"""
    generator = LabelReportGenerator()
    
    sample_pr_details["labels"] = [
        {"name": "test-label", "color": "ff0000"}
    ]
    
    label_groups = generator.group_prs_by_label([sample_pr_details])
    
    assert "test-label" in label_groups
    assert len(label_groups["test-label"]) == 1
    assert label_groups["test-label"][0] == sample_pr_details


def test_generate_label_markdown(tmp_path):
    """ラベルマークダウンの生成テスト"""
    generator = LabelReportGenerator()
    
    prs = [
        {
            "basic_info": {
                "number": 1,
                "title": "Open PR",
                "html_url": "https://github.com/test/test/pull/1"
            },
            "state": "open",
            "labels": [{"name": "test-label"}]
        },
        {
            "basic_info": {
                "number": 2,
                "title": "Closed PR",
                "html_url": "https://github.com/test/test/pull/2"
            },
            "state": "closed",
            "labels": [{"name": "test-label"}]
        }
    ]
    
    output_file = tmp_path / "test-label.md"
    
    markdown = generator.generate_label_markdown("test-label", prs, output_file)
    
    assert "# test-label" in markdown
    assert "## オープン (1件)" in markdown
    assert "## クローズド (1件)" in markdown
    assert "PR #1" in markdown
    assert "PR #2" in markdown
    assert output_file.exists()


def test_generate_label_index(tmp_path):
    """ラベルインデックスの生成テスト"""
    generator = LabelReportGenerator()
    
    label_groups = {
        "label-a": [{"basic_info": {"number": 1}}],
        "label-b": [{"basic_info": {"number": 2}}, {"basic_info": {"number": 3}}],
        "unlabeled": [{"basic_info": {"number": 4}}]
    }
    
    output_file = tmp_path / "index.md"
    
    index = generator.generate_label_index(label_groups, output_file)
    
    assert "# ラベル一覧" in index
    assert "label-a.md" in index
    assert "label-b.md" in index
    assert "unlabeled.md" in index
    assert "(1件)" in index
    assert "(2件)" in index
    assert output_file.exists()


def test_load_pr_data_from_directory(temp_data_dir, sample_pr_details):
    """ディレクトリからPRデータを読み込むテスト"""
    generator = LabelReportGenerator()
    
    pr_file = temp_data_dir / "1.json"
    with open(pr_file, "w", encoding="utf-8") as f:
        json.dump(sample_pr_details, f)
    
    pr_data = generator.load_pr_data_from_directory(temp_data_dir)
    
    assert len(pr_data) == 1
    assert pr_data[0]["basic_info"]["number"] == sample_pr_details["basic_info"]["number"]
    assert pr_data[0]["basic_info"]["title"] == sample_pr_details["basic_info"]["title"]


def test_generate_reports(temp_data_dir, sample_pr_details, tmp_path):
    """レポート生成のテスト"""
    generator = LabelReportGenerator()
    
    pr_file = temp_data_dir / "1.json"
    with open(pr_file, "w", encoding="utf-8") as f:
        sample_pr_details["labels"] = [{"name": "test-label"}]
        json.dump(sample_pr_details, f)
    
    output_dir = tmp_path / "reports"
    
    result = generator.generate_reports(temp_data_dir, output_dir)
    
    assert result is True
    assert (output_dir / "test-label.md").exists()
    assert (output_dir / "index.md").exists()
