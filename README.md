# 【アーカイブ済み】PR分析システム

⚠️ **重要なお知らせ**: このリポジトリの機能は [policy-pr-hub](https://github.com/team-mirai-volunteer/policy-pr-hub) に移行されました。

## 移行について

このリポジトリ（pr_analysis）の役割は [team-mirai-volunteer/policy-pr-hub](https://github.com/team-mirai-volunteer/policy-pr-hub) に移行され、後者がまともに動き始めています。

**新しいシステムの特徴:**
- より包括的なPR分析機能
- GitHub Actionsによる自動化された定期実行
- 1700+件の政策改善提案PRに対応
- セクション分析、ラベル分析、政策分野別分析などの高度な分析機能
- データ収集の自動化とRate Limit対応

**今後の利用について:**
- 新しい開発や分析作業は [policy-pr-hub](https://github.com/team-mirai-volunteer/policy-pr-hub) をご利用ください
- このリポジトリは参考資料として保持されますが、アクティブな開発は行われません
- このリポジトリはpublic archiveとして保存される予定です

---

# PR分析システム（旧版）

GitHubのPull Requestデータを収集・分析し、レポートを生成するシステムです。

## 機能

- GitHub APIを使用したPRデータの収集
- PRごとのファイル単位でのデータ保存
- ラベルごとのPR分析レポート生成
- セクション（マークダウン見出し）ごとのPR分析
- GitHub Actionsによる定期実行（1時間ごと）

## リポジトリ構成

このシステムは2つのリポジトリで構成されています：

1. **pr_analysis**: コード、テスト、GitHub Actionsワークフローを含むリポジトリ
2. **pr-data**: データのみを含むリポジトリ（PRデータ、インデックス、レポート）

### コードの配置場所

コードは以下のように配置する必要があります：

- `src/collectors`: PRデータ収集モジュール
- `src/analyzers`: PRデータ分析モジュール
- `src/generators`: レポート生成モジュール
- `src/utils`: ユーティリティ関数
- `scripts`: データ移行スクリプトなどのユーティリティスクリプト
- `config`: 設定ファイル
- `tests`: テストコード
- `.github/workflows`: GitHub Actionsワークフロー定義

### データの配置場所

データは**pr-data**リポジトリに以下のように配置されます：

- `prs/`: PRごとのJSONファイル
- `indexes/by_label/`: ラベルごとのPRインデックス
- `indexes/by_section/`: セクションごとのPRインデックス
- `reports/labels/`: ラベルごとのレポート
- `reports/sections/`: セクションごとのレポート

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

### データ移行スクリプト

既存の単一JSONファイルからPRごとのファイル形式にデータを移行するには：

```bash
python scripts/migrate_data.py --input /path/to/merged_prs_data.json --output-dir /path/to/pr-data
```

### GitHub Actionsでの実行

リポジトリに`.github/workflows/hourly_update.yml`を設定することで、1時間ごとに自動実行されます。
このワークフローは以下の処理を行います：

1. pr_analysisリポジトリのチェックアウト
2. pr-dataリポジトリのチェックアウト
3. PRデータの収集と保存
4. ラベルレポートの生成
5. セクション分析レポートの生成
6. pr-dataリポジトリへの変更のコミットとプッシュ

## テスト

```bash
pytest
```

## ライセンス

[LICENSE](LICENSE)ファイルを参照してください。
