# New Relic Playground

New Relic の主要機能を Python（FastAPI）で検証するための playground リポジトリ。

## 技術スタック

| カテゴリ | 技術 |
|----------|------|
| 言語 | Python 3.12+ |
| Web フレームワーク | FastAPI + uvicorn |
| APM | New Relic Python Agent |
| コンテナ | Docker / Docker Compose |
| テスト | pytest |

## ディレクトリ構成

```
new-relic-playground/
├── CLAUDE.md                    # Claude Code 用プロジェクト指示書
├── README.md                    # プロジェクトインデックス（本ファイル）
├── rules/                       # 開発ルール・規約
│   ├── development-process.md   # 開発プロセス・ワークフロー
│   ├── coding-standards.md      # コーディング規約
│   └── architecture.md          # アーキテクチャ方針
├── specs/                       # 検証仕様書（本プロジェクトの存在理由を定義する永続ドキュメント）
│   ├── 00-overview.md           # 仕様全体の概要
│   ├── 01-app-structure.md      # アプリケーション構成仕様
│   ├── 02-docker.md             # Docker 構成仕様
│   ├── 03-newrelic-agent-setup.md # New Relic エージェント設定仕様
│   ├── 04-apm-basic.md          # APM 基本機能の検証仕様
│   ├── 05-custom-instrumentation.md # カスタム計装の検証仕様
│   ├── 06-distributed-tracing.md    # 分散トレーシングの検証仕様
│   ├── 07-error-tracking.md     # エラートラッキングの検証仕様
│   ├── 08-logs-in-context.md    # Logs in Context の検証仕様
│   ├── 09-custom-events-metrics.md  # カスタムイベント・メトリクスの検証仕様
│   └── 10-verification-checklist.md # 総合検証チェックリスト
├── app/                         # アプリケーションコード（実装時に作成）
├── tests/                       # テストコード（実装時に作成）
├── docker-compose.yml           # Docker Compose 設定（実装時に作成）
└── Dockerfile                   # Docker ビルド設定（実装時に作成）
```

### specs/ について

`specs/` は本プロジェクトの**永続的な仕様書**を格納するディレクトリ。New Relic の各機能に対する検証仕様を定義しており、プロジェクトの存在理由そのものを表すドキュメント群である。実装コードはこの仕様に基づいて作成される。

### rules/ について

`rules/` は開発時のルール・規約を格納するディレクトリ。コーディング規約、開発プロセス、アーキテクチャ方針など、「どう作るか」を定義する。

## ドキュメント一覧

### 開発ルール（rules/）

| ファイル | 内容 |
|----------|------|
| [development-process.md](rules/development-process.md) | 開発プロセス・ワークフロー |
| [coding-standards.md](rules/coding-standards.md) | コーディング規約 |
| [architecture.md](rules/architecture.md) | アーキテクチャ方針 |

### 検証仕様（specs/）

| ファイル | 内容 | 優先度 |
|----------|------|--------|
| [00-overview.md](specs/00-overview.md) | 仕様全体の概要 | - |
| [01-app-structure.md](specs/01-app-structure.md) | アプリケーション構成仕様 | 必須 |
| [02-docker.md](specs/02-docker.md) | Docker 構成仕様 | 必須 |
| [03-newrelic-agent-setup.md](specs/03-newrelic-agent-setup.md) | New Relic エージェント設定仕様 | 必須 |
| [04-apm-basic.md](specs/04-apm-basic.md) | APM 基本機能の検証仕様 | 必須 |
| [05-custom-instrumentation.md](specs/05-custom-instrumentation.md) | カスタム計装の検証仕様 | 推奨 |
| [06-distributed-tracing.md](specs/06-distributed-tracing.md) | 分散トレーシングの検証仕様 | 推奨 |
| [07-error-tracking.md](specs/07-error-tracking.md) | エラートラッキングの検証仕様 | 必須 |
| [08-logs-in-context.md](specs/08-logs-in-context.md) | Logs in Context の検証仕様 | 推奨 |
| [09-custom-events-metrics.md](specs/09-custom-events-metrics.md) | カスタムイベント・メトリクスの検証仕様 | 推奨 |
| [10-verification-checklist.md](specs/10-verification-checklist.md) | 総合検証チェックリスト | - |

## クイックスタート

### 前提条件

- Docker / Docker Compose がインストール済み
- New Relic アカウントとライセンスキーを取得済み

### 環境構築・起動

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd new-relic-playground

# 2. 環境変数を設定
cp .env.example .env
# .env に NEW_RELIC_LICENSE_KEY を設定

# 3. Docker Compose で起動
docker compose up --build

# 4. 動作確認
curl http://localhost:8000/health
```

### New Relic UI での確認

1. [New Relic One](https://one.newrelic.com) にログイン
2. APM > Services から対象アプリケーションを選択
3. 各仕様の検証手順に従い動作を確認
