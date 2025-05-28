#!/usr/bin/env python3
"""
セクション分析器のテスト
"""

import pytest
from unittest.mock import patch

from src.analyzers.section_analyzer import SectionAnalyzer


def test_extract_sections_from_patch():
    """パッチからセクションを抽出するテスト"""
    analyzer = SectionAnalyzer()
    
    patch_content = """@@ -1,5 +1,10 @@
 
-## 古いセクション
+## 新しいセクション
 
 テスト内容
+
+## 追加セクション
+
+新しい内容
"""
    
    sections = analyzer.extract_sections_from_patch(patch_content)
    
    assert len(sections) == 2
    assert sections[0]["title"] == "新しいセクション"
    assert sections[0]["level"] == 2
    assert sections[1]["title"] == "追加セクション"
    assert sections[1]["level"] == 2


def test_analyze_pr_files(sample_pr_details):
    """PRファイルの分析テスト"""
    analyzer = SectionAnalyzer()
    
    sample_pr_details["files"][0]["patch"] = """@@ -1,5 +1,10 @@
 
-## 古いセクション
+## 新しいセクション
 
 テスト内容
+
+## 追加セクション
+
+新しい内容
"""
    
    sections_info = analyzer.analyze_pr_files(sample_pr_details)
    
    assert len(sections_info) == 1
    assert sections_info[0]["filename"] == "test.md"
    assert len(sections_info[0]["sections"]) == 2
    assert sections_info[0]["sections"][0]["title"] == "新しいセクション"
    assert sections_info[0]["sections"][1]["title"] == "追加セクション"


def test_analyze_prs(sample_pr_details):
    """複数PRの分析テスト"""
    analyzer = SectionAnalyzer()
    
    sample_pr_details["files"][0]["patch"] = """@@ -1,5 +1,10 @@
 
-## 古いセクション
+## 新しいセクション
 
 テスト内容
+
+## 追加セクション
+
+新しい内容
"""
    
    results = analyzer.analyze_prs([sample_pr_details])
    
    assert "新しいセクション" in results
    assert "追加セクション" in results
    assert len(results["新しいセクション"]) == 1
    assert results["新しいセクション"][0]["number"] == 1
    assert results["新しいセクション"][0]["filename"] == "test.md"


def test_generate_section_report(tmp_path):
    """セクションレポート生成テスト"""
    analyzer = SectionAnalyzer()
    
    section_results = {
        "セクション1": [
            {"number": 1, "title": "PR 1", "url": "https://github.com/test/test/pull/1", "filename": "file1.md"},
            {"number": 2, "title": "PR 2", "url": "https://github.com/test/test/pull/2", "filename": "file2.md"}
        ],
        "セクション2": [
            {"number": 3, "title": "PR 3", "url": "https://github.com/test/test/pull/3", "filename": "file3.md"}
        ]
    }
    
    output_file = tmp_path / "section_report.md"
    
    report = analyzer.generate_section_report(section_results, output_file)
    
    assert "# セクション別PR分析レポート" in report
    assert "## セクション1" in report
    assert "## セクション2" in report
    assert "PR #1" in report
    assert "PR #2" in report
    assert "PR #3" in report
    assert output_file.exists()
