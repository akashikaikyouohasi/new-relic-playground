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
async def variable_endpoint(
    delay_ms: int = Query(default=500, ge=0, le=10000),
) -> dict:
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
    return {
        "status": "ok",
        "message": "cpu intensive task completed",
        "result": result,
        "elapsed_ms": elapsed_ms,
    }


def _fibonacci(n: int) -> int:
    # フィボナッチ数列を再帰で計算
    if n <= 1:
        return n
    return _fibonacci(n - 1) + _fibonacci(n - 2)
