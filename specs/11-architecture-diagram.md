# 構成図仕様

## 概要

プロジェクト全体のアーキテクチャを draw.io 形式の構成図として作成する。
Client からアプリケーション、外部サービス、New Relic One までのデータフローを可視化し、
プロジェクトの全体像を一目で把握できるようにする。

## コンポーネント一覧

### 外部コンポーネント（上部）

| コンポーネント | 説明 |
|---------------|------|
| Client (User/curl) | API にリクエストを送るクライアント |

### 内部コンポーネント（Docker コンテナ内）

| コンポーネント | 説明 |
|---------------|------|
| newrelic-admin | New Relic Agent のプロセスラッパー |
| uvicorn :8000 | ASGI サーバー |
| FastAPI App | Web アプリケーション本体 |
| health.py | `GET /health` |
| apm.py | `GET /api/apm/fast`, `/slow`, `/variable`, `/cpu-intensive` |
| errors.py | `GET /api/errors/unhandled`, `/handled`, `/http-error`, `POST /api/errors/custom-error` |
| tracing.py | `GET /api/tracing/external-call`, `/chained-calls`, `/parallel-calls` |
| custom.py | `GET /api/custom-instrumentation/function-trace`, `/custom-attributes`, `POST /api/custom-instrumentation/background-task` |
| logs.py | `GET /api/logs/basic`, `/structured`, `/with-error` |
| custom_events.py | `POST /api/custom/event`, `/metric`, `/batch-events` |
| New Relic Python Agent | 計装レイヤー（全リクエストを自動計装） |

### 外部コンポーネント（右側・下部）

| コンポーネント | 説明 |
|---------------|------|
| httpbin.org | 外部 API 呼び出し先（tracing.py が使用） |
| New Relic One (one.newrelic.com) | テレメトリデータの送信先 |

## データフロー定義

| # | From | To | プロトコル | ラベル/説明 |
|---|------|-----|-----------|------------|
| 1 | Client | FastAPI App | HTTP :8000 | API リクエスト |
| 2 | tracing.py | httpbin.org | HTTPS | 外部 API 呼び出し（httpx） |
| 3 | New Relic Python Agent | New Relic One | HTTPS | APM Transactions |
| 4 | New Relic Python Agent | New Relic One | HTTPS | Distributed Tracing (Spans) |
| 5 | New Relic Python Agent | New Relic One | HTTPS | Error Events |
| 6 | New Relic Python Agent | New Relic One | HTTPS | Logs (Logs in Context) |
| 7 | New Relic Python Agent | New Relic One | HTTPS | Custom Events / Metrics |

## レイアウト

```
Client (User/curl)
    |
    | HTTP :8000
    v
+-- Docker Container (python:3.12-slim) ----------------+
|                                                        |
|  newrelic-admin → uvicorn :8000                        |
|       └── FastAPI App                                  |
|           ├── health.py       GET /health              |
|           ├── apm.py          GET /api/apm/*           |
|           ├── errors.py       GET|POST /api/errors/*   |
|           ├── tracing.py      GET /api/tracing/*  -----+--> httpbin.org
|           ├── custom.py       GET|POST /api/custom-*   |    (HTTPS, httpx)
|           ├── logs.py         GET /api/logs/*          |
|           └── custom_events.py POST /api/custom/*      |
|                                                        |
|  New Relic Python Agent (計装レイヤー)                 |
+-----+--------------------------------------------------+
      |
      | HTTPS
      | - APM Transactions
      | - Distributed Tracing (Spans)
      | - Error Events
      | - Logs (Logs in Context)
      | - Custom Events / Metrics
      v
New Relic One (one.newrelic.com)
```

## 受け入れ基準

- [ ] `docs/architecture.drawio` が作成されていること
- [ ] draw.io アプリで正常に開けること
- [ ] 全ルーター（7 ファイル）が図に含まれていること
- [ ] Docker コンテナの境界が明示されていること
- [ ] Client → App → 外部 API のデータフローが描画されていること
- [ ] App → New Relic One のテレメトリデータフローが描画されていること
- [ ] 各データフローに通信プロトコルとデータ種別がラベル付けされていること
