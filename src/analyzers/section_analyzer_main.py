#!/usr/bin/env python3
"""
PRのセクション分析スクリプト

PRで変更されたマークダウンファイルのセクション（見出し）を分析します。
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analyzers.section_analyzer import SectionAnalyzer
from src.utils.github_api import load_config


def parse_arguments():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description="PRのセクション分析スクリプト")
    parser.add_argument(
        "--input", type=str, help="入力ファイルまたはディレクトリ（設定ファイルの値を上書き）"
    )
    parser.add_argument(
        "--output", type=str, help="出力ファイル（設定ファイルの値を上書き）"
    )
    return parser.parse_args()


def load_pr_data_from_directory(input_dir):
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


def main():
    """メイン関数"""
    args = parse_arguments()
    
    config = load_config()
    
    input_path = args.input
    if not input_path:
        input_path = Path(config["data"]["base_dir"])
    
    output_file = args.output
    if not output_file:
        output_dir = Path(config["data"]["reports_dir"]) / "sections"
        os.makedirs(output_dir, exist_ok=True)
        output_file = output_dir / "section_report.md"
    
    if Path(input_path).is_dir():
        pr_data = load_pr_data_from_directory(input_path)
    else:
        try:
            with open(input_path, encoding="utf-8") as f:
                pr_data = json.load(f)
        except Exception as e:
            print(f"PRデータの読み込み中にエラーが発生しました: {e}")
            return 1
    
    if not pr_data:
        print("PRデータがありません")
        return 1
    
    analyzer = SectionAnalyzer(config)
    
    section_results = analyzer.analyze_prs(pr_data)
    
    analyzer.generate_section_report(section_results, output_file)
    
    print(f"セクションレポートを {output_file} に生成しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
