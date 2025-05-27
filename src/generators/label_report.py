#!/usr/bin/env python3
"""
ラベルごとのレポート生成モジュール

PRデータからラベルごとのマークダウンレポートを生成します。
"""

import json
import os
from collections import defaultdict
from pathlib import Path

from ..utils.github_api import load_config


class LabelReportGenerator:
    """ラベルごとのレポートを生成するクラス"""
    
    def __init__(self, config=None):
        """初期化"""
        self.config = config or load_config()
        
    def load_pr_data(self, input_file):
        """PRデータをJSONファイルから読み込む"""
        try:
            with open(input_file, encoding="utf-8") as f:
                pr_data = json.load(f)
            print(f"{len(pr_data)}件のPRデータを読み込みました")
            return pr_data
        except Exception as e:
            print(f"PRデータの読み込み中にエラーが発生しました: {e}")
            return []
            
    def load_pr_data_from_directory(self, input_dir):
        """PRデータをディレクトリから読み込む（ファイルごとのPRデータ）"""
        pr_data = []
        input_path = Path(input_dir)
        
        if not input_path.exists() or not input_path.is_dir():
            print(f"ディレクトリが存在しません: {input_dir}")
            return []
            
        json_files = list(input_path.glob("*.json"))
        print(f"{len(json_files)}件のPRデータファイルを見つけました")
        
        for json_file in json_files:
            try:
                with open(json_file, encoding="utf-8") as f:
                    pr = json.load(f)
                    pr_data.append(pr)
            except Exception as e:
                print(f"{json_file}の読み込み中にエラーが発生しました: {e}")
                
        return pr_data
        
    def group_prs_by_label(self, pr_data):
        """PRをラベルごとにグループ化する"""
        label_groups = defaultdict(list)
        unlabeled_prs = []
        
        for pr in pr_data:
            if not pr:  # Noneの場合はスキップ
                continue
                
            labels = pr.get("labels", [])
            
            if not labels:
                unlabeled_prs.append(pr)
                continue
                
            for label in labels:
                label_name = label.get("name")
                if label_name:
                    label_groups[label_name].append(pr)
                    
        if unlabeled_prs:
            label_groups["unlabeled"] = unlabeled_prs
            
        return label_groups
        
    def generate_label_markdown(self, label_name, prs, output_file=None):
        """特定のラベルに関するマークダウンレポートを生成する"""
        if not prs:
            return f"# {label_name}\n\nこのラベルのPRはありません。\n"
            
        if label_name == "unlabeled":
            title = "ラベルなし"
        else:
            title = label_name
            
        markdown = f"# {title}\n\n"
        
        open_prs = [pr for pr in prs if pr.get("state") == "open"]
        closed_prs = [pr for pr in prs if pr.get("state") == "closed"]
        
        if open_prs:
            markdown += f"## オープン ({len(open_prs)}件)\n\n"
            for pr in open_prs:
                basic_info = pr.get("basic_info", {})
                pr_number = basic_info.get("number", "?")
                pr_title = basic_info.get("title", "タイトルなし")
                pr_url = basic_info.get("html_url", "#")
                
                markdown += f"- [PR #{pr_number}]({pr_url}) {pr_title}\n"
            markdown += "\n"
            
        if closed_prs:
            markdown += f"## クローズド ({len(closed_prs)}件)\n\n"
            for pr in closed_prs:
                basic_info = pr.get("basic_info", {})
                pr_number = basic_info.get("number", "?")
                pr_title = basic_info.get("title", "タイトルなし")
                pr_url = basic_info.get("html_url", "#")
                
                markdown += f"- [PR #{pr_number}]({pr_url}) {pr_title}\n"
            markdown += "\n"
            
        if output_file:
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown)
            print(f"ラベル '{label_name}' のレポートを {output_file} に保存しました")
            
        return markdown
        
    def generate_label_index(self, label_groups, output_file=None):
        """ラベルの一覧インデックスを生成する"""
        if not label_groups:
            return "# ラベル一覧\n\nラベルがありません。\n"
            
        markdown = "# ラベル一覧\n\n"
        
        sorted_labels = sorted(label_groups.keys(), key=lambda x: (x == "unlabeled", x.lower()))
        
        for label_name in sorted_labels:
            prs = label_groups[label_name]
            pr_count = len(prs)
            
            if label_name == "unlabeled":
                display_name = "ラベルなし"
            else:
                display_name = label_name
                
            filename = label_name.lower().replace(" ", "-")
            
            markdown += f"- [{display_name}]({filename}.md) ({pr_count}件)\n"
            
        if output_file:
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown)
            print(f"ラベルインデックスを {output_file} に保存しました")
            
        return markdown
        
    def generate_reports(self, input_data, output_dir):
        """すべてのラベルレポートを生成する"""
        if isinstance(input_data, (str, Path)) and Path(input_data).is_file():
            pr_data = self.load_pr_data(input_data)
        elif isinstance(input_data, (str, Path)) and Path(input_data).is_dir():
            pr_data = self.load_pr_data_from_directory(input_data)
        else:
            pr_data = input_data
            
        if not pr_data:
            print("PRデータがありません")
            return False
            
        label_groups = self.group_prs_by_label(pr_data)
        
        if not label_groups:
            print("ラベルグループがありません")
            return False
            
        os.makedirs(output_dir, exist_ok=True)
        
        for label_name, prs in label_groups.items():
            filename = label_name.lower().replace(" ", "-")
            output_file = os.path.join(output_dir, f"{filename}.md")
            
            self.generate_label_markdown(label_name, prs, output_file)
            
        index_file = os.path.join(output_dir, "index.md")
        self.generate_label_index(label_groups, index_file)
        
        return True
