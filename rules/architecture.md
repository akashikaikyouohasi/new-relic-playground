# アーキテクチャ方針

## システム構成

Docker Compose で以下のサービスを構成する。

```
┌─────────────────────────────────────────────────┐
│ Docker Compose                                   │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ app (primary-app)                            │ │
│  │                                               │ │
│  │  Python 3.12 + FastAPI + uvicorn             │ │
│  │  New Relic Python Agent                      │ │
│  │                                               │ │
│  │  起動: newrelic-admin run-program             │ │
│  │        uvicorn app.main:app                  │ │
│  │  ポート: 8000                                 │ │
│  └───────────────┬─────────────────────────────┘ │
│                  │                                 │
│                  │ データ送信                      │
│                  ▼                                 │
│         New Relic Collector                        │
│         (collector.newrelic.com)                   │
└─────────────────────────────────────────────────┘
```

### 将来の拡張構成

分散トレーシングの検証時に以下を追加予定:

```
┌─────────────────────────────────────────────────┐
│ Docker Compose                                   │
│                                                   │
│  ┌──────────────┐     ┌──────────────┐          │
│  │ app          │────▶│ secondary-app│          │
│  │ (FastAPI)    │     │ (FastAPI)    │          │
│  │ :8000        │     │ :8001        │          │
│  └──────────────┘     └──────────────┘          │
│                                                   │
│  ┌──────────────┐                                │
│  │ db           │  ← 必要に応じて追加            │
│  │ (PostgreSQL) │                                │
│  │ :5432        │                                │
│  └──────────────┘                                │
└─────────────────────────────────────────────────┘
```

## アプリケーション層構成

```
app/
├── main.py          # FastAPI アプリ初期化、Router 登録
├── config.py        # 設定管理（環境変数の読み込み）
├── routers/         # API エンドポイント定義（プレゼンテーション層）
│   ├── health.py    # GET /health
│   ├── apm.py       # /api/apm/* エンドポイント群
│   ├── tracing.py   # /api/tracing/* エンドポイント群
│   ├── errors.py    # /api/errors/* エンドポイント群
│   └── custom.py    # /api/custom/* エンドポイント群
├── services/        # ビジネスロジック（サービス層）
└── utils/           # 共通ユーティリティ
```

### 各層の責務

| 層 | ディレクトリ | 責務 |
|----|-------------|------|
| プレゼンテーション | `routers/` | HTTP リクエストの受信、バリデーション、レスポンス返却 |
| サービス | `services/` | ビジネスロジック、外部 API 呼び出し、New Relic カスタム計装 |
| ユーティリティ | `utils/` | 汎用的なヘルパー関数 |

## データフロー

### 通常のリクエストフロー

```
クライアント
  │
  │ HTTP リクエスト
  ▼
FastAPI (uvicorn)
  │
  │ ミドルウェア（New Relic Agent 自動計装）
  ▼
Router
  │
  │ ビジネスロジック呼び出し
  ▼
Service
  │
  │ 処理実行
  ▼
Router
  │
  │ JSON レスポンス
  ▼
クライアント
```

### New Relic Agent の動作

New Relic Python Agent は以下を自動的に行う:

1. **トランザクション計測**: 各 HTTP リクエストを自動的にトランザクションとして記録
2. **レスポンスタイム**: 処理時間を自動計測
3. **エラーキャプチャ**: 未処理の例外を自動収集
4. **外部呼び出し**: `httpx` / `requests` による外部 HTTP 呼び出しを自動追跡

## New Relic Agent の統合ポイント

### 起動方法

`newrelic-admin` コマンドを使用して uvicorn を起動する:

```bash
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 設定ファイル（newrelic.ini）

```ini
[newrelic]
app_name = new-relic-playground
license_key = %(NEW_RELIC_LICENSE_KEY)s

distributed_tracing.enabled = true
application_logging.enabled = true
application_logging.forwarding.enabled = true

log_file = /tmp/newrelic-python-agent.log
log_level = info
```

### 環境変数

| 変数 | 説明 | 設定場所 |
|------|------|----------|
| `NEW_RELIC_LICENSE_KEY` | ライセンスキー | `.env` |
| `NEW_RELIC_APP_NAME` | アプリケーション名（オーバーライド用） | `.env`（任意） |
| `NEW_RELIC_LOG_LEVEL` | エージェントログレベル | `.env`（任意） |

## 設計原則

- **シンプルさ優先**: 検証目的のプロジェクトであり、過度な抽象化は行わない
- **仕様との対応を明確に**: 各エンドポイントがどの仕様に対応するか分かるようにする
- **自動計装を最大活用**: カスタム計装は必要な箇所のみに限定する
- **本番環境の模倣**: Docker Compose を用いて、本番に近い構成で検証する
