#!/usr/bin/env python3
"""
ラベルごとのレポート生成スクリプト

PRデータからラベルごとのマークダウンレポートを生成します。
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.generators.label_report import LabelReportGenerator
from src.utils.github_api import load_config


def parse_arguments():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description="ラベルごとのレポート生成スクリプト")
    parser.add_argument(
        "--input", type=str, help="入力ファイルまたはディレクトリ（設定ファイルの値を上書き）"
    )
    parser.add_argument(
        "--output-dir", type=str, help="出力ディレクトリ（設定ファイルの値を上書き）"
    )
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_arguments()
    
    config = load_config()
    
    input_path = args.input
    if not input_path:
        input_path = Path(config["data"]["base_dir"])
    
    output_dir = args.output_dir
    if not output_dir:
        output_dir = Path(config["data"]["reports_dir"]) / "labels"
    
    generator = LabelReportGenerator(config)
    
    success = generator.generate_reports(input_path, output_dir)
    
    if success:
        print(f"ラベルレポートを {output_dir} に生成しました")
        return 0
    else:
        print("ラベルレポートの生成に失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
