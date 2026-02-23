# 09: カスタムイベント・メトリクスの検証仕様

## 概要

New Relic のカスタムイベントとカスタムメトリクスの送信機能を検証する。`record_custom_event()` でビジネスイベントを、`record_custom_metric()` でカスタムメトリクスを New Relic に送信し、NRQL で集計・可視化できることを確認する。

## 検証用エンドポイント

### POST /api/custom/event

カスタムイベントを New Relic に送信する。

- **リクエストボディ**:
  ```json
  {
    "event_type": "UserAction",
    "attributes": {
      "action": "purchase",
      "product_id": "prod-789",
      "amount": 2500,
      "currency": "JPY"
    }
  }
  ```
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "custom event recorded",
    "event_type": "UserAction"
  }
  ```

### POST /api/custom/metric

カスタムメトリクスを New Relic に送信する。

- **リクエストボディ**:
  ```json
  {
    "metric_name": "Custom/BusinessMetric/OrderProcessingTime",
    "value": 1250.5
  }
  ```
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "custom metric recorded",
    "metric_name": "Custom/BusinessMetric/OrderProcessingTime",
    "value": 1250.5
  }
  ```

### POST /api/custom/batch-events

複数のカスタムイベントを一括送信する。ダッシュボード検証用にまとまったデータを生成する。

- **リクエストボディ**:
  ```json
  {
    "event_type": "PageView",
    "count": 50
  }
  ```
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "batch events recorded",
    "event_type": "PageView",
    "count": 50
  }
  ```

## 実装ガイド

### カスタムイベントの送信

```python
import newrelic.agent

@router.post("/event")
async def record_event(body: CustomEventRequest) -> dict:
    newrelic.agent.record_custom_event(body.event_type, body.attributes)
    return {
        "status": "ok",
        "message": "custom event recorded",
        "event_type": body.event_type,
    }
```

### カスタムメトリクスの送信

```python
import newrelic.agent

@router.post("/metric")
async def record_metric(body: CustomMetricRequest) -> dict:
    newrelic.agent.record_custom_metric(body.metric_name, body.value)
    return {
        "status": "ok",
        "message": "custom metric recorded",
        "metric_name": body.metric_name,
        "value": body.value,
    }
```

### バッチイベントの生成

```python
import random
import newrelic.agent

@router.post("/batch-events")
async def batch_events(body: BatchEventRequest) -> dict:
    for _ in range(body.count):
        attributes = {
            "page": random.choice(["/home", "/products", "/cart", "/checkout"]),
            "duration_ms": random.randint(100, 5000),
            "user_agent": random.choice(["Chrome", "Firefox", "Safari"]),
        }
        newrelic.agent.record_custom_event(body.event_type, attributes)
    return {
        "status": "ok",
        "message": "batch events recorded",
        "event_type": body.event_type,
        "count": body.count,
    }
```

### イベント命名規則

| 種別 | 命名パターン | 例 |
|------|-------------|-----|
| カスタムイベント | PascalCase | `UserAction`, `PageView`, `OrderCompleted` |
| カスタムメトリクス | `Custom/<Category>/<Name>` | `Custom/BusinessMetric/OrderProcessingTime` |

## 検証手順

### 1. カスタムイベントの送信

```bash
# 単一イベント
curl -X POST http://localhost:8000/api/custom/event \
  -H "Content-Type: application/json" \
  -d '{"event_type": "UserAction", "attributes": {"action": "purchase", "product_id": "prod-789", "amount": 2500, "currency": "JPY"}}'

# バッチイベント
curl -X POST http://localhost:8000/api/custom/batch-events \
  -H "Content-Type: application/json" \
  -d '{"event_type": "PageView", "count": 50}'
```

### 2. カスタムメトリクスの送信

```bash
curl -X POST http://localhost:8000/api/custom/metric \
  -H "Content-Type: application/json" \
  -d '{"metric_name": "Custom/BusinessMetric/OrderProcessingTime", "value": 1250.5}'
```

### 3. New Relic UI での確認

1. **Query Your Data**: NRQL でカスタムイベントを検索
2. **Dashboards**: カスタムイベントを使ったダッシュボードが作成可能であること
3. **Metrics Explorer**: カスタムメトリクスが表示されること

## NRQL クエリ

```sql
-- カスタムイベント: UserAction
SELECT * FROM UserAction
WHERE appName = 'new-relic-playground'
SINCE 30 minutes ago

-- カスタムイベント: 金額の集計
SELECT sum(amount), average(amount), count(*)
FROM UserAction
WHERE appName = 'new-relic-playground' AND action = 'purchase'
SINCE 1 hour ago

-- カスタムイベント: PageView のページ別集計
SELECT count(*), average(duration_ms)
FROM PageView
WHERE appName = 'new-relic-playground'
FACET page
SINCE 30 minutes ago

-- カスタムメトリクス
SELECT average(newrelic.timeslice.value)
FROM Metric
WHERE metricTimesliceName = 'Custom/BusinessMetric/OrderProcessingTime'
SINCE 30 minutes ago
TIMESERIES

-- カスタムイベントの件数推移
SELECT count(*) FROM UserAction
WHERE appName = 'new-relic-playground'
SINCE 1 hour ago
TIMESERIES 5 minutes
```

## 受け入れ基準

- [ ] `record_custom_event()` で送信したイベントが NRQL で取得できる
- [ ] カスタムイベントの属性（amount, product_id 等）が正しく記録される
- [ ] `record_custom_metric()` で送信したメトリクスが Metrics Explorer に表示される
- [ ] バッチイベントが正しい件数分記録される
- [ ] カスタムイベントを使った NRQL の集計・FACET クエリが実行できる
