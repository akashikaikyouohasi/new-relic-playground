# CLAUDE.md - プロジェクト指示書

このファイルは Claude Code がプロジェクトを理解するための指示書である。

## プロジェクト概要

New Relic の主要機能を Python（FastAPI）で検証する playground プロジェクト。
プロジェクト全体の構成・ドキュメント一覧は [README.md](README.md) を参照すること。

## 技術スタック

- **言語**: Python 3.12+
- **Web フレームワーク**: FastAPI + uvicorn
- **APM**: New Relic Python Agent (`newrelic` パッケージ)
- **コンテナ**: Docker / Docker Compose
- **テスト**: pytest
- **リンター/フォーマッター**: ruff

## 実装時のディレクトリ構成

```
app/
├── main.py              # FastAPI アプリケーションのエントリポイント
├── routers/             # API エンドポイント定義
│   ├── health.py        # ヘルスチェック
│   ├── apm.py           # APM 基本検証用
│   ├── tracing.py       # 分散トレーシング検証用
│   ├── errors.py        # エラートラッキング検証用
│   └── custom.py        # カスタムイベント・メトリクス検証用
├── services/            # ビジネスロジック
├── utils/               # ユーティリティ
└── config.py            # 設定管理

tests/
├── conftest.py
└── test_*.py

newrelic.ini             # New Relic Agent 設定ファイル
Dockerfile
docker-compose.yml
.env.example             # 環境変数テンプレート
requirements.txt
```

## 開発ルール

### 仕様駆動開発

1. コード生成の前に、必ず `specs/` 配下の仕様書を作成または更新すること
2. 仕様書が存在しない機能のコードを書いてはならない
3. 仕様書に定義されたエンドポイント・検証手順に従って実装すること
4. 実装完了後は `specs/10-verification-checklist.md` のチェックリストを更新すること

### コーディング規約

`rules/coding-standards.md` に従うこと。主要ポイント:

- PEP 8 準拠（ruff でフォーマット）
- 型ヒントを必須とする
- FastAPI の Depends を活用した依存性注入
- Python 標準の logging モジュールで構造化ログを出力
- 実装完了後、コミット前に `uv run ruff format . && uv run ruff check --fix .` を実行すること

### アーキテクチャ

`rules/architecture.md` に従うこと。

### 意思決定ログ

- 技術選定・設計方針・ツール選定など、判断を伴う決定を行った場合は `decisions/` に ADR を記録すること
- ファイル名: `NNNN-<slug>.md`（連番 + 英語スラッグ）
- テンプレート: `decisions/TEMPLATE.md` に従う
- 後から判断基準の妥当性を検証できるよう、背景・選択肢・決定理由を必ず記載すること

### 開発プロセス

`rules/development-process.md` に従うこと。

## Makefile ルール

- セットアップが必要な作業（ツールのインストール・初期化など）は必ず `Makefile` のターゲットとして定義すること
- 新しいセットアップ手順を追加した場合は `make setup` ターゲットにも反映すること
- 利用可能なターゲットは `make help` で確認できる

## New Relic 設定の注意事項

- **ライセンスキーは絶対にコミットしない**: 環境変数 `NEW_RELIC_LICENSE_KEY` で渡す
- `newrelic.ini` にはプレースホルダーのみ記載し、実際のキーは `.env` ファイルで管理
- `.env` ファイルは `.gitignore` に追加済みであること
- New Relic Agent の起動は `newrelic-admin run-program` コマンドを使用

## セキュリティルール

- シークレット（API キー、ライセンスキー等）をソースコードにハードコードしない
- `.env` ファイルをコミットしない（`.gitignore` で除外）
- Docker イメージに機密情報を含めない（ビルド時の ARG ではなくランタイムの ENV を使用）
- 外部 API 呼び出し時の URL はハードコードせず環境変数で管理
