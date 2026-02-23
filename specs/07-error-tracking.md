# 07: エラートラッキングの検証仕様

## 概要

New Relic のエラートラッキング機能を検証する。未処理例外の自動キャプチャ、`notice_error()` による手動エラー通知、カスタムアトリビュート付きエラーの記録を確認する。

## 検証用エンドポイント

### GET /api/errors/unhandled

未処理の例外を発生させ、New Relic が自動キャプチャすることを検証する。

- **処理内容**: 意図的に例外を raise する
- **期待レスポンス**: HTTP 500
  ```json
  {
    "detail": "Internal Server Error"
  }
  ```

### GET /api/errors/handled

例外をキャッチして処理しつつ、`notice_error()` で New Relic に通知する。

- **レスポンス**: HTTP 200
  ```json
  {
    "status": "ok",
    "message": "error was handled and reported to New Relic",
    "error_class": "ValueError"
  }
  ```

### GET /api/errors/http-error?status_code={status_code}

指定した HTTP ステータスコードのエラーを返す。

- **パラメータ**: `status_code`（400, 403, 404, 500 等）
- **期待レスポンス**: 指定したステータスコード
  ```json
  {
    "detail": "Simulated error with status 404"
  }
  ```

### POST /api/errors/custom-error

カスタムアトリビュート付きのエラーを New Relic に通知する。

- **リクエストボディ**:
  ```json
  {
    "error_message": "Payment processing failed",
    "user_id": "user-123",
    "order_id": "order-456"
  }
  ```
- **レスポンス**: HTTP 200
  ```json
  {
    "status": "ok",
    "message": "custom error reported to New Relic",
    "attributes": {
      "user_id": "user-123",
      "order_id": "order-456"
    }
  }
  ```

## 実装ガイド

### 未処理例外

```python
@router.get("/unhandled")
async def unhandled_error() -> dict:
    raise RuntimeError("This is an unhandled error for testing")
```

### notice_error の使用

```python
import newrelic.agent

@router.get("/handled")
async def handled_error() -> dict:
    try:
        raise ValueError("This is a handled error")
    except ValueError:
        newrelic.agent.notice_error()
    return {
        "status": "ok",
        "message": "error was handled and reported to New Relic",
        "error_class": "ValueError",
    }
```

### カスタムアトリビュート付きエラー

```python
import newrelic.agent

@router.post("/custom-error")
async def custom_error(body: ErrorRequest) -> dict:
    try:
        raise Exception(body.error_message)
    except Exception:
        newrelic.agent.notice_error(attributes={
            "user_id": body.user_id,
            "order_id": body.order_id,
        })
    return {
        "status": "ok",
        "message": "custom error reported to New Relic",
        "attributes": {"user_id": body.user_id, "order_id": body.order_id},
    }
```

## 検証手順

### 1. 各エンドポイントにリクエスト

```bash
# 未処理例外
curl http://localhost:8000/api/errors/unhandled

# ハンドル済みエラー
curl http://localhost:8000/api/errors/handled

# HTTP エラー
curl "http://localhost:8000/api/errors/http-error?status_code=404"
curl "http://localhost:8000/api/errors/http-error?status_code=500"

# カスタムエラー
curl -X POST http://localhost:8000/api/errors/custom-error \
  -H "Content-Type: application/json" \
  -d '{"error_message": "Payment failed", "user_id": "user-123", "order_id": "order-456"}'
```

### 2. New Relic UI での確認

1. **APM > Errors inbox**: エラーが一覧に表示されること
2. **APM > Errors > Error traces**: エラーのスタックトレースが確認できること
3. **APM > Errors > Error analytics**: エラー率やエラーの分布が表示されること

## NRQL クエリ

```sql
-- エラー一覧
SELECT * FROM TransactionError
WHERE appName = 'new-relic-playground'
SINCE 30 minutes ago

-- エラークラス別の件数
SELECT count(*) FROM TransactionError
WHERE appName = 'new-relic-playground'
FACET error.class
SINCE 30 minutes ago

-- カスタムアトリビュート付きエラー
SELECT error.message, user_id, order_id
FROM TransactionError
WHERE appName = 'new-relic-playground' AND user_id IS NOT NULL
SINCE 30 minutes ago

-- エラー率
SELECT percentage(count(*), WHERE error IS true) as 'Error Rate'
FROM Transaction
WHERE appName = 'new-relic-playground'
SINCE 30 minutes ago
TIMESERIES
```

## 受け入れ基準

- [ ] 未処理例外が New Relic に自動キャプチャされる
- [ ] `notice_error()` で通知したエラーが記録される
- [ ] HTTP エラー（4xx, 5xx）がエラーとして記録される
- [ ] カスタムアトリビュート付きエラーの属性が NRQL で取得できる
- [ ] Errors inbox にエラーが表示される
- [ ] エラーのスタックトレースが確認できる
