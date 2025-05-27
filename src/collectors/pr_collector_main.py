#!/usr/bin/env python3
"""
PRデータ収集スクリプト

GitHub APIを使用してPRデータを収集し、ファイルごとに保存します。
"""

import argparse
import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.collectors.pr_collector import PRCollector
from src.utils.github_api import load_config


def parse_arguments():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description="PRデータ収集スクリプト")
    parser.add_argument(
        "--limit", type=int, default=0, help="取得するPRの最大数（0は無制限）"
    )
    parser.add_argument(
        "--output-dir", type=str, help="出力ディレクトリ（設定ファイルの値を上書き）"
    )
    parser.add_argument(
        "--state", type=str, default="all", choices=["open", "closed", "all"],
        help="取得するPRの状態（open/closed/all）"
    )
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_arguments()
    
    config = load_config()
    
    output_dir = args.output_dir
    if not output_dir:
        output_dir = Path(config["data"]["base_dir"])
    
    collector = PRCollector(config)
    
    last_run_file = Path(output_dir).parent / "last_run_info.json"
    last_updated_at = None
    
    if last_run_file.exists():
        import json
        try:
            with open(last_run_file, encoding="utf-8") as f:
                last_run_info = json.load(f)
                last_updated_at = datetime.datetime.fromisoformat(last_run_info["last_updated_at"])
                print(f"前回の実行情報を読み込みました: 最終更新日時 = {last_updated_at}")
        except Exception as e:
            print(f"前回の実行情報の読み込み中にエラーが発生しました: {e}")
    
    updated_prs = collector.update_pr_data(
        limit=args.limit if args.limit > 0 else None,
        last_updated_at=last_updated_at,
        output_dir=output_dir
    )
    
    if updated_prs:
        now = datetime.datetime.now()
        last_run_info = {
            "last_updated_at": now.isoformat(),
            "timestamp": now.isoformat(),
            "updated_count": len(updated_prs)
        }
        
        os.makedirs(last_run_file.parent, exist_ok=True)
        with open(last_run_file, "w", encoding="utf-8") as f:
            import json
            json.dump(last_run_info, f, ensure_ascii=False, indent=2)
        print(f"最後の実行情報を {last_run_file} に保存しました")
    
    print(f"合計 {len(updated_prs)} 件のPRを更新しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
