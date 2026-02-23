# 06: 分散トレーシングの検証仕様

## 概要

New Relic の分散トレーシング機能を検証する。サービス間の HTTP 呼び出しにおいて、トレースコンテキストが伝播され、エンドツーエンドのトレースが New Relic UI で確認できることを確認する。

## 前提

- `newrelic.ini` で `distributed_tracing.enabled = true` が設定されていること（03 で設定済み）
- 分散トレーシングの完全な検証には secondary-app が必要（後述）

## 検証用エンドポイント

### GET /api/tracing/external-call

外部 HTTP サービスへの呼び出しを行い、外部呼び出しのトレースを検証する。

- **処理内容**: `httpx` を使用して外部 API を呼び出す
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "external call completed",
    "external_status_code": 200,
    "elapsed_ms": 150
  }
  ```

### GET /api/tracing/chained-calls

複数の外部呼び出しを連鎖させ、トレースの深さを検証する。

- **処理内容**: 複数の外部 API を順番に呼び出す
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "chained calls completed",
    "calls": [
      {"url": "https://httpbin.org/get", "status": 200, "elapsed_ms": 120},
      {"url": "https://httpbin.org/delay/1", "status": 200, "elapsed_ms": 1050}
    ]
  }
  ```

### GET /api/tracing/parallel-calls

並列の外部呼び出しを行い、並行処理のトレースを検証する。

- **処理内容**: `asyncio.gather()` で複数の外部 API を並列に呼び出す
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "parallel calls completed",
    "total_elapsed_ms": 300,
    "calls": [
      {"url": "https://httpbin.org/get", "status": 200},
      {"url": "https://httpbin.org/get", "status": 200}
    ]
  }
  ```

### GET /api/tracing/service-to-service（拡張: secondary-app 導入後）

primary-app から secondary-app への呼び出しを行い、サービス間の分散トレースを検証する。

- **処理内容**: primary-app → secondary-app への HTTP 呼び出し
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "service-to-service call completed",
    "primary_app": "new-relic-playground",
    "secondary_app_response": { ... }
  }
  ```

## 実装ガイド

### 外部呼び出し（httpx 使用）

```python
import httpx

async def call_external_api(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return {"url": url, "status": response.status_code}
```

New Relic Python Agent は `httpx` の呼び出しを自動計装する。分散トレースヘッダー（`traceparent`, `tracestate`）も自動で付与される。

### secondary-app の構成（拡張時）

`docker-compose.yml` にサービスを追加:

```yaml
services:
  app:
    # ... 既存の設定
  secondary-app:
    build:
      context: .
      dockerfile: Dockerfile.secondary
    ports:
      - "8001:8001"
    env_file:
      - .env
    environment:
      - NEW_RELIC_CONFIG_FILE=newrelic-secondary.ini
      - NEW_RELIC_APP_NAME=new-relic-playground-secondary
```

## 検証手順

### 1. 外部呼び出しの検証

```bash
curl http://localhost:8000/api/tracing/external-call
curl http://localhost:8000/api/tracing/chained-calls
curl http://localhost:8000/api/tracing/parallel-calls
```

### 2. New Relic UI での確認

1. **APM > Distributed Tracing**: トレースマップにアプリケーションと外部サービスが表示されること
2. **APM > Transactions > Transaction trace**: 外部呼び出しがトレースのセグメントとして表示されること
3. **APM > External services**: 呼び出し先の外部サービスが一覧に表示されること

## NRQL クエリ

```sql
-- 分散トレースの確認
SELECT * FROM Span
WHERE appName = 'new-relic-playground'
SINCE 30 minutes ago
LIMIT 100

-- 外部呼び出しの確認
SELECT * FROM Span
WHERE appName = 'new-relic-playground' AND category = 'http'
SINCE 30 minutes ago

-- トレース ID でのフィルタリング
SELECT * FROM Span
WHERE trace.id = '<trace-id>'
SINCE 1 hour ago

-- 外部サービスのレスポンスタイム
SELECT average(duration)
FROM Span
WHERE appName = 'new-relic-playground' AND span.kind = 'client'
FACET peer.hostname
SINCE 30 minutes ago
```

## 受け入れ基準

- [ ] 外部 HTTP 呼び出しが Span として New Relic に記録される
- [ ] 連鎖的な呼び出しが一つのトレースとして紐付けられる
- [ ] 並列呼び出しがトレース内で並行セグメントとして表示される
- [ ] Distributed Tracing 画面でトレースマップが表示される
- [ ] External services 画面に呼び出し先が表示される
- [ ] NRQL で Span データを取得できる
