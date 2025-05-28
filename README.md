# PR Analysis System

GitHubのPull Requestデータを収集・分析し、レポートを生成するシステムです。

## 機能

- GitHub APIを使用したPRデータの収集
- PRごとのファイル単位でのデータ保存
- ラベルごとのPR分析レポート生成
- セクション（マークダウン見出し）ごとのPR分析
- GitHub Actionsによる定期実行（1時間ごと）

## 構成

- `src/collectors`: PRデータ収集モジュール
- `src/analyzers`: PRデータ分析モジュール
- `src/generators`: レポート生成モジュール
- `src/utils`: ユーティリティ関数
- `config`: 設定ファイル
- `tests`: テストコード

## 設定

`config/settings.yaml`で以下の設定が可能です：

```yaml
github:
  repo_owner: "team-mirai"  # 対象リポジトリのオーナー
  repo_name: "policy"       # 対象リポジトリ名
  token_env_var: "GITHUB_TOKEN"  # GitHubトークンの環境変数名
  api_base_url: "https://api.github.com"  # GitHub API URL

data:
  storage_type: "file_per_pr"  # データ保存形式（file_per_pr: PRごとのファイル）
  pr_data_repo: "team-mirai-volunteer/pr-data"  # データ保存用リポジトリ
  base_dir: "prs"  # PRデータ保存ディレクトリ
  indexes_dir: "indexes"  # インデックスディレクトリ
  reports_dir: "reports"  # レポートディレクトリ

api:
  retry_count: 3  # APIリクエスト失敗時の再試行回数
  rate_limit_wait: true  # レート制限に達した場合に待機するか
  request_delay: 0.5  # APIリクエスト間の待機時間（秒）

collectors:
  update_interval: 3600  # 更新間隔（秒）
  max_workers: 10  # 並列処理時のワーカー数
```

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

### PRデータの収集

```python
from src.collectors.pr_collector import PRCollector

collector = PRCollector()
collector.update_pr_data(limit=100)  # 最新100件のPRを取得
```

### GitHub Actionsでの実行

リポジトリに`.github/workflows/hourly_update.yml`を設定することで、1時間ごとに自動実行されます。

## テスト

```bash
pytest
```

## ライセンス

[LICENSE](LICENSE)ファイルを参照してください。
