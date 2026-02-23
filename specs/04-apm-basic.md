# 04: APM 基本機能の検証仕様

## 概要

New Relic APM の基本機能を検証する。トランザクション計測、レスポンスタイム、スループット、Apdex スコアなどの基本メトリクスが正しく収集されることを確認する。

## 検証用エンドポイント

### GET /api/apm/fast

即座にレスポンスを返すエンドポイント。正常系のベースライン計測用。

- **期待レスポンスタイム**: < 100ms
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "fast response",
    "elapsed_ms": 5
  }
  ```

### GET /api/apm/slow

意図的に遅延を入れたエンドポイント。レスポンスタイム計測の検証用。

- **遅延**: 2 秒（`asyncio.sleep(2)`）
- **期待レスポンスタイム**: ~2000ms
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "slow response",
    "elapsed_ms": 2003
  }
  ```

### GET /api/apm/variable?delay_ms={delay_ms}

可変遅延エンドポイント。レスポンスタイム分布の検証用。

- **パラメータ**: `delay_ms`（整数、ミリ秒単位の遅延）
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "variable response",
    "requested_delay_ms": 500,
    "elapsed_ms": 503
  }
  ```

### GET /api/apm/cpu-intensive

CPU 負荷をかけるエンドポイント。CPU 時間の計測検証用。

- **処理内容**: フィボナッチ数列の計算等
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "message": "cpu intensive task completed",
    "result": 832040,
    "elapsed_ms": 150
  }
  ```

## 実装ガイド

### routers/apm.py

```python
import asyncio
import time

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/apm", tags=["apm"])

@router.get("/fast")
async def fast_endpoint() -> dict:
    start = time.time()
    elapsed_ms = int((time.time() - start) * 1000)
    return {"status": "ok", "message": "fast response", "elapsed_ms": elapsed_ms}

@router.get("/slow")
async def slow_endpoint() -> dict:
    start = time.time()
    await asyncio.sleep(2)
    elapsed_ms = int((time.time() - start) * 1000)
    return {"status": "ok", "message": "slow response", "elapsed_ms": elapsed_ms}

@router.get("/variable")
async def variable_endpoint(delay_ms: int = Query(default=500, ge=0, le=10000)) -> dict:
    start = time.time()
    await asyncio.sleep(delay_ms / 1000)
    elapsed_ms = int((time.time() - start) * 1000)
    return {
        "status": "ok",
        "message": "variable response",
        "requested_delay_ms": delay_ms,
        "elapsed_ms": elapsed_ms,
    }

@router.get("/cpu-intensive")
async def cpu_intensive_endpoint() -> dict:
    start = time.time()
    result = _fibonacci(30)
    elapsed_ms = int((time.time() - start) * 1000)
    return {"status": "ok", "message": "cpu intensive task completed", "result": result, "elapsed_ms": elapsed_ms}

def _fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return _fibonacci(n - 1) + _fibonacci(n - 2)
```

## 検証手順

### 1. トランザクション計測

```bash
# 各エンドポイントにリクエスト
curl http://localhost:8000/api/apm/fast
curl http://localhost:8000/api/apm/slow
curl http://localhost:8000/api/apm/variable?delay_ms=1000
curl http://localhost:8000/api/apm/cpu-intensive
```

### 2. New Relic UI での確認

1. **APM > Summary**: トランザクション数、レスポンスタイム、スループットが表示されること
2. **APM > Transactions**: 各エンドポイントのトランザクションが個別に記録されていること
3. **APM > Transactions > Transaction traces**: slow エンドポイントのトレースが記録されていること

### 3. Apdex の確認

- `/api/apm/fast` は Satisfied（S）に分類されること
- `/api/apm/slow` は Frustrated（F）に分類されること（デフォルト Apdex T=0.5s の場合）

## NRQL クエリ

```sql
-- トランザクション一覧
SELECT name, duration, httpResponseCode
FROM Transaction
WHERE appName = 'new-relic-playground'
SINCE 30 minutes ago

-- エンドポイント別の平均レスポンスタイム
SELECT average(duration)
FROM Transaction
WHERE appName = 'new-relic-playground'
FACET name
SINCE 30 minutes ago

-- スループット（RPM）
SELECT rate(count(*), 1 minute) as 'RPM'
FROM Transaction
WHERE appName = 'new-relic-playground'
SINCE 30 minutes ago
TIMESERIES

-- Apdex スコア
SELECT apdex(duration, 0.5) as 'Apdex'
FROM Transaction
WHERE appName = 'new-relic-playground'
SINCE 30 minutes ago

-- slow エンドポイントのレスポンスタイム分布
SELECT histogram(duration, 10, 20)
FROM Transaction
WHERE appName = 'new-relic-playground' AND name LIKE '%/slow%'
SINCE 30 minutes ago
```

## 受け入れ基準

- [ ] `/api/apm/fast` のトランザクションが New Relic に記録される
- [ ] `/api/apm/slow` のレスポンスタイムが ~2 秒で記録される
- [ ] `/api/apm/variable` のレスポンスタイムが指定した遅延に対応する
- [ ] `/api/apm/cpu-intensive` のトランザクションが記録される
- [ ] APM Summary にスループットが表示される
- [ ] トランザクショントレースが記録されている
- [ ] NRQL クエリでデータが取得できる
