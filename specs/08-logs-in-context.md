# 08: Logs in Context の検証仕様

## 概要

New Relic の Logs in Context 機能を検証する。Python の `logging` モジュールから出力されるログに `trace.id` や `span.id` が自動的に付与され、ログとトレースが紐付けられることを確認する。

## 前提

- `newrelic.ini` で以下が設定されていること（03 で設定済み）:
  ```ini
  application_logging.enabled = true
  application_logging.forwarding.enabled = true
  application_logging.metrics.enabled = true
  ```

## 検証用エンドポイント

### GET /api/logs/basic

基本的なログ出力を行い、ログが New Relic に転送されることを検証する。

- **処理内容**: 各ログレベルでログを出力
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "logs emitted at all levels",
    "levels": ["debug", "info", "warning", "error"]
  }
  ```

### GET /api/logs/structured

構造化ログ（extra フィールド付き）を出力し、属性付きログが New Relic に転送されることを検証する。

- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "structured logs emitted",
    "attributes": {
      "user_id": "user-123",
      "action": "profile_view",
      "duration_ms": 45
    }
  }
  ```

### GET /api/logs/with-error

エラーを発生させつつログを出力し、エラートレースとログが同じ `trace.id` で紐付けられることを検証する。

- **レスポンス**: HTTP 200
  ```json
  {
    "status": "ok",
    "message": "error logged and reported",
    "trace_context": "check New Relic for trace.id correlation"
  }
  ```

## 実装ガイド

### ロギング設定

```python
import logging

# main.py でロギングを設定
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
```

New Relic Agent がロギングハンドラーを自動的にインストルメントし、`trace.id` と `span.id` をログレコードに追加する。

### ログ出力の実装

```python
import logging

logger = logging.getLogger(__name__)

@router.get("/basic")
async def basic_logs() -> dict:
    logger.debug("Debug level log message")
    logger.info("Info level log message")
    logger.warning("Warning level log message")
    logger.error("Error level log message")
    return {
        "status": "ok",
        "message": "logs emitted at all levels",
        "levels": ["debug", "info", "warning", "error"],
    }
```

### 構造化ログ

```python
@router.get("/structured")
async def structured_logs() -> dict:
    logger.info(
        "User action recorded",
        extra={"user_id": "user-123", "action": "profile_view", "duration_ms": 45},
    )
    return {
        "status": "ok",
        "message": "structured logs emitted",
        "attributes": {"user_id": "user-123", "action": "profile_view", "duration_ms": 45},
    }
```

## 検証手順

### 1. ログを生成

```bash
curl http://localhost:8000/api/logs/basic
curl http://localhost:8000/api/logs/structured
curl http://localhost:8000/api/logs/with-error
```

### 2. New Relic UI での確認

1. **Logs**: ログが一覧に表示されること
2. **Logs > Attributes**: `trace.id`, `span.id`, `service.name` が含まれていること
3. **APM > Transactions > Logs**: トランザクションに紐付いたログが表示されること
4. **APM > Distributed Tracing > トレース詳細 > Logs**: トレースに紐付いたログが表示されること

### 3. ログとトレースの紐付け確認

1. ログエントリの `trace.id` をコピー
2. Distributed Tracing で同じ `trace.id` のトレースを検索
3. 両者が一致していることを確認

## NRQL クエリ

```sql
-- ログ一覧
SELECT * FROM Log
WHERE service.name = 'new-relic-playground'
SINCE 30 minutes ago

-- trace.id 付きログの確認
SELECT message, trace.id, span.id, level
FROM Log
WHERE service.name = 'new-relic-playground' AND trace.id IS NOT NULL
SINCE 30 minutes ago

-- ログレベル別件数
SELECT count(*) FROM Log
WHERE service.name = 'new-relic-playground'
FACET level
SINCE 30 minutes ago

-- 特定トレースに紐付くログ
SELECT timestamp, level, message
FROM Log
WHERE trace.id = '<trace-id>'
SINCE 1 hour ago
ORDER BY timestamp

-- ログの属性を確認
SELECT message, user_id, action, duration_ms
FROM Log
WHERE service.name = 'new-relic-playground' AND user_id IS NOT NULL
SINCE 30 minutes ago
```

## 受け入れ基準

- [ ] Python `logging` モジュールのログが New Relic に転送される
- [ ] ログに `trace.id` と `span.id` が自動付与されている
- [ ] APM のトランザクション詳細からログを参照できる
- [ ] Distributed Tracing のトレース詳細からログを参照できる
- [ ] 構造化ログの extra フィールドがログ属性として記録される
- [ ] NRQL でログデータを取得できる
