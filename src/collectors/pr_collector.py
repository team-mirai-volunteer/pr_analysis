#!/usr/bin/env python3
"""
PRデータ収集モジュール

GitHubからPRデータを収集し、ファイルごとに保存します。
"""

import datetime
import json
import os
import time
from pathlib import Path

import yaml
from tqdm import tqdm

from ..utils.github_api import (
    make_github_api_request,
    check_rate_limit,
    wait_for_rate_limit_reset,
    load_config
)


class PRCollector:
    """PRデータを収集するクラス"""
    
    def __init__(self, config=None):
        """初期化"""
        self.config = config or load_config()
        self.api_base_url = self.config["github"]["api_base_url"]
        self.repo_owner = self.config["github"]["repo_owner"]
        self.repo_name = self.config["github"]["repo_name"]
        
        self.storage_type = self.config["data"]["storage_type"]
        self.base_dir = Path(self.config["data"]["base_dir"])
        
        self.request_delay = self.config["api"]["request_delay"]
        self.rate_limit_wait = self.config["api"]["rate_limit_wait"]
        
    def get_pull_requests(self, limit=None, sort_by="updated", direction="desc", last_updated_at=None, state="all"):
        """Pull Requestを取得する

        Args:
            limit: 取得するPRの最大数
            sort_by: ソート基準 ("created", "updated", "popularity", "long-running")
            direction: ソート方向 ("asc" or "desc")
            last_updated_at: 前回実行時の最新更新日時（この日時以降のPRのみ取得）
            state: PRの状態 ("open", "closed", "all")
        """
        all_prs = []
        page = 1
        per_page = 100

        while True:
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls"
            params = {"state": state, "per_page": per_page, "page": page, "sort": sort_by, "direction": direction}

            try:
                prs = make_github_api_request(url, params=params)
                if not prs:
                    break

                if last_updated_at:
                    new_prs = []
                    for pr in prs:
                        pr_updated_at = datetime.datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00"))
                        if pr_updated_at <= last_updated_at:
                            print(f"前回処理済みのPR #{pr['number']} に到達しました。処理を終了します。")
                            break
                        new_prs.append(pr)

                    if len(new_prs) < len(prs):
                        all_prs.extend(new_prs)
                        break

                    all_prs.extend(new_prs)
                else:
                    all_prs.extend(prs)

                page += 1

                if limit and len(all_prs) >= limit:
                    all_prs = all_prs[:limit]
                    break

                if page > 1 and self.request_delay > 0:
                    time.sleep(self.request_delay)  # APIレート制限を考慮して少し待機
                    
            except Exception as e:
                print(f"PRリスト取得中にエラーが発生しました (ページ {page}): {e}")
                break

        return all_prs
    
    def get_pr_by_number(self, pr_number):
        """PR番号を指定してPRの基本情報を取得する"""
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        try:
            return make_github_api_request(url)
        except Exception as e:
            if hasattr(e, 'response') and e.response.status_code == 404:
                print(f"PR #{pr_number} は存在しません")
                return None
            raise
    
    def get_pr_comments(self, pr_number):
        """PRのコメントを取得する"""
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/comments"
        return make_github_api_request(url)

    def get_pr_review_comments(self, pr_number):
        """PRのレビューコメントを取得する"""
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/comments"
        return make_github_api_request(url)

    def get_pr_commits(self, pr_number):
        """PRのコミット情報を取得する"""
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/commits"
        return make_github_api_request(url)

    def get_pr_files(self, pr_number):
        """PRの変更ファイル情報を取得する"""
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/files"
        return make_github_api_request(url)

    def get_pr_labels(self, pr_number):
        """PRのラベル情報を取得する"""
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_number}/labels"
        return make_github_api_request(url)
    
    def get_pr_details(self, pr_number, include_comments=True, include_review_comments=True, 
                      include_commits=True, include_files=True, include_labels=True):
        """PRの詳細情報を取得する（オプションで取得する情報を選択可能）"""
        pr_data = self.get_pr_by_number(pr_number)
        if not pr_data:
            return None

        pr_details = {
            "basic_info": pr_data,
            "state": pr_data["state"],  # open または closed
            "updated_at": pr_data["updated_at"],  # 更新日時を保存
        }

        if include_labels:
            try:
                pr_details["labels"] = self.get_pr_labels(pr_number)
            except Exception as e:
                print(f"PR #{pr_number} のラベル取得中にエラーが発生しました: {str(e)[:200]}")
                pr_details["labels"] = []

        if include_comments:
            try:
                pr_details["comments"] = self.get_pr_comments(pr_number)
            except Exception as e:
                print(f"PR #{pr_number} のコメント取得中にエラーが発生しました: {str(e)[:200]}")
                pr_details["comments"] = []

        if include_review_comments:
            try:
                pr_details["review_comments"] = self.get_pr_review_comments(pr_number)
            except Exception as e:
                print(f"PR #{pr_number} のレビューコメント取得中にエラーが発生しました: {str(e)[:200]}")
                pr_details["review_comments"] = []

        if include_commits:
            try:
                pr_details["commits"] = self.get_pr_commits(pr_number)
            except Exception as e:
                print(f"PR #{pr_number} のコミット取得中にエラーが発生しました: {str(e)[:200]}")
                pr_details["commits"] = []

        if include_files:
            try:
                pr_details["files"] = self.get_pr_files(pr_number)
            except Exception as e:
                print(f"PR #{pr_number} のファイル取得中にエラーが発生しました: {str(e)[:200]}")
                pr_details["files"] = []

        return pr_details
    
    def save_pr_to_file(self, pr_data, output_dir=None):
        """PRデータを個別のJSONファイルに保存する"""
        if not pr_data or "basic_info" not in pr_data:
            print("保存するPRデータがありません")
            return False
            
        pr_number = pr_data["basic_info"]["number"]
        output_dir = output_dir or self.base_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{pr_number}.json"
        filepath = Path(output_dir) / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(pr_data, f, ensure_ascii=False, indent=2)
            
        print(f"PR #{pr_number} のデータを {filepath} に保存しました")
        return True
    
    def update_pr_data(self, limit=None, last_updated_at=None, output_dir=None):
        """PRデータを更新する"""
        remaining, reset_time = check_rate_limit()
        if remaining < 100 and self.rate_limit_wait:
            print(f"API制限が残り少ないため ({remaining} リクエスト)、リセット時間まで待機します")
            wait_for_rate_limit_reset(reset_time)
        
        print("最新のPRを取得しています...")
        prs = self.get_pull_requests(limit=limit, last_updated_at=last_updated_at)
        print(f"{len(prs)}件の新しいPRを取得しました")
        
        if not prs:
            print("更新するPRがありません")
            return []
            
        updated_prs = []
        for pr in tqdm(prs, desc="PRデータ取得"):
            try:
                pr_number = pr["number"]
                pr_details = self.get_pr_details(pr_number)
                
                if pr_details:
                    self.save_pr_to_file(pr_details, output_dir)
                    updated_prs.append(pr_details)
                    
                if self.request_delay > 0:
                    time.sleep(self.request_delay)
                    
            except Exception as e:
                print(f"PR #{pr['number']} の処理中にエラーが発生しました: {e}")
                
        return updated_prs
