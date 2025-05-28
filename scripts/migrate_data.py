#!/usr/bin/env python3
"""
データ移行スクリプト

team-mirai/random リポジトリの merged_prs_data.json から
team-mirai-volunteer/pr-data リポジトリのファイルごとのPRデータ形式に変換します。
"""

import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict


def load_json_file(file_path):
    """JSONファイルを読み込む"""
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []


def save_json_file(data, file_path):
    """JSONファイルを保存する"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"データを保存しました: {file_path}")
        return True
    except Exception as e:
        print(f"データ保存中にエラーが発生しました {file_path}: {e}")
        return False


def create_label_index(pr_data):
    """ラベルごとのPR番号インデックスを作成する"""
    label_index = defaultdict(list)
    
    for pr in pr_data:
        if not pr:
            continue
            
        pr_number = pr.get("basic_info", {}).get("number")
        if not pr_number:
            continue
            
        if pr.get("labels"):
            for label in pr.get("labels", []):
                label_name = label.get("name")
                if label_name and pr_number not in label_index[label_name]:
                    label_index[label_name].append(pr_number)
        
        if "basic_info" in pr and pr["basic_info"].get("labels"):
            for label in pr["basic_info"]["labels"]:
                label_name = label.get("name")
                if label_name and pr_number not in label_index[label_name]:
                    label_index[label_name].append(pr_number)
    
    return dict(label_index)


def create_section_index(pr_data):
    """セクションごとのPR番号インデックスを作成する"""
    section_index = defaultdict(list)
    
    for pr in pr_data:
        if not pr:
            continue
            
        pr_number = pr.get("basic_info", {}).get("number")
        if not pr_number:
            continue
            
        if pr.get("section_info"):
            for section in pr.get("section_info", []):
                section_name = section.get("section")
                if section_name and pr_number not in section_index[section_name]:
                    section_index[section_name].append(pr_number)
    
    return dict(section_index)


def migrate_data(input_file, output_dir):
    """データを移行する"""
    pr_data = load_json_file(input_file)
    if not pr_data:
        print(f"入力ファイル {input_file} からデータを読み込めませんでした")
        return False
    
    print(f"{len(pr_data)}件のPRデータを読み込みました")
    
    prs_dir = Path(output_dir) / "prs"
    indexes_dir = Path(output_dir) / "indexes"
    label_index_dir = indexes_dir / "by_label"
    section_index_dir = indexes_dir / "by_section"
    
    os.makedirs(prs_dir, exist_ok=True)
    os.makedirs(label_index_dir, exist_ok=True)
    os.makedirs(section_index_dir, exist_ok=True)
    
    success_count = 0
    for pr in pr_data:
        if not pr:
            continue
            
        pr_number = pr.get("basic_info", {}).get("number")
        if not pr_number:
            continue
            
        pr_file = prs_dir / f"{pr_number}.json"
        if save_json_file(pr, pr_file):
            success_count += 1
    
    print(f"{success_count}/{len(pr_data)}件のPRデータを保存しました")
    
    label_index = create_label_index(pr_data)
    for label_name, pr_numbers in label_index.items():
        label_file = label_index_dir / f"{label_name}.json"
        save_json_file(pr_numbers, label_file)
    
    print(f"{len(label_index)}件のラベルインデックスを作成しました")
    
    section_index = create_section_index(pr_data)
    for section_name, pr_numbers in section_index.items():
        safe_section_name = section_name.replace("/", "_").replace("\\", "_").replace(":", "_")
        section_file = section_index_dir / f"{safe_section_name}.json"
        save_json_file(pr_numbers, section_file)
    
    print(f"{len(section_index)}件のセクションインデックスを作成しました")
    
    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="PRデータを単一JSONからファイルごとのフォーマットに変換します")
    parser.add_argument("--input", required=True, help="入力JSONファイルのパス")
    parser.add_argument("--output-dir", default=".", help="出力ディレクトリのパス")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"入力ファイル {args.input} が見つかりません")
        return 1
    
    if migrate_data(args.input, args.output_dir):
        print("データ移行が完了しました")
        return 0
    else:
        print("データ移行に失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
