# 05: カスタム計装の検証仕様

## 概要

New Relic Python Agent のカスタム計装機能を検証する。自動計装では取得できない詳細なパフォーマンスデータを、手動で計装することで収集する。`function_trace`、`background_task`、カスタムアトリビュートの付与を検証する。

## 検証用エンドポイント

### GET /api/custom-instrumentation/function-trace

`@function_trace()` デコレータを使用して、内部関数の実行時間を個別に計測する。

- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "function trace demo",
    "steps": ["step_a: 100ms", "step_b: 200ms", "step_c: 50ms"]
  }
  ```

### POST /api/custom-instrumentation/background-task

`@background_task()` デコレータを使用して、バックグラウンドタスクとしてトランザクションを記録する。

- **リクエストボディ**:
  ```json
  {
    "task_name": "data_processing",
    "items": 100
  }
  ```
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "background task started",
    "task_name": "data_processing"
  }
  ```

### GET /api/custom-instrumentation/custom-attributes

`newrelic.agent.add_custom_attributes()` を使用して、トランザクションにカスタムアトリビュートを付与する。

- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "custom attributes added",
    "attributes": {
      "user_tier": "premium",
      "feature_flag": "new_dashboard",
      "request_priority": "high"
    }
  }
  ```

## 実装ガイド

### function_trace の使用

```python
import newrelic.agent

@newrelic.agent.function_trace(name="step_a")
def step_a() -> str:
    time.sleep(0.1)
    return "step_a: 100ms"

@newrelic.agent.function_trace(name="step_b")
def step_b() -> str:
    time.sleep(0.2)
    return "step_b: 200ms"
```

### background_task の使用

```python
import newrelic.agent

@newrelic.agent.background_task(name="data_processing")
def process_data(items: int) -> None:
    # バックグラウンド処理
    for i in range(items):
        time.sleep(0.01)
```

### カスタムアトリビュートの付与

```python
import newrelic.agent

newrelic.agent.add_custom_attributes([
    ("user_tier", "premium"),
    ("feature_flag", "new_dashboard"),
    ("request_priority", "high"),
])
```

## 検証手順

### 1. function_trace の検証

```bash
curl http://localhost:8000/api/custom-instrumentation/function-trace
```

New Relic UI:
1. **APM > Transactions** で該当トランザクションを選択
2. **Transaction trace** を確認し、`step_a`, `step_b`, `step_c` が個別のセグメントとして表示されること

### 2. background_task の検証

```bash
curl -X POST http://localhost:8000/api/custom-instrumentation/background-task \
  -H "Content-Type: application/json" \
  -d '{"task_name": "data_processing", "items": 100}'
```

New Relic UI:
1. **APM > Transactions** のタブを **Non-web** に切り替え
2. `data_processing` がバックグラウンドトランザクションとして記録されていること

### 3. カスタムアトリビュートの検証

```bash
curl http://localhost:8000/api/custom-instrumentation/custom-attributes
```

## NRQL クエリ

```sql
-- function_trace のセグメント確認
SELECT * FROM Span
WHERE appName = 'new-relic-playground' AND name LIKE 'Function/step_%'
SINCE 30 minutes ago

-- バックグラウンドタスクの確認
SELECT * FROM Transaction
WHERE appName = 'new-relic-playground' AND transactionType = 'Other'
SINCE 30 minutes ago

-- カスタムアトリビュートの確認
SELECT user_tier, feature_flag, request_priority
FROM Transaction
WHERE appName = 'new-relic-playground' AND user_tier IS NOT NULL
SINCE 30 minutes ago
```

## 受け入れ基準

- [ ] `function_trace` で内部関数が個別セグメントとしてトレースに表示される
- [ ] `background_task` が Non-web トランザクションとして記録される
- [ ] カスタムアトリビュートがトランザクションに付与されている
- [ ] NRQL でカスタムアトリビュートを使ったクエリが実行できる
