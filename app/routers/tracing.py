import asyncio
import time

import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/tracing", tags=["tracing"])

HTTPBIN_BASE = "https://httpbin.org"


async def _call_external(client: httpx.AsyncClient, url: str) -> dict:
    start = time.time()
    response = await client.get(url)
    elapsed_ms = int((time.time() - start) * 1000)
    return {"url": url, "status": response.status_code, "elapsed_ms": elapsed_ms}


@router.get("/external-call")
async def external_call() -> dict:
    start = time.time()
    async with httpx.AsyncClient(timeout=10.0) as client:
        result = await _call_external(client, f"{HTTPBIN_BASE}/get")
    elapsed_ms = int((time.time() - start) * 1000)
    return {
        "status": "ok",
        "message": "external call completed",
        "external_status_code": result["status"],
        "elapsed_ms": elapsed_ms,
    }


@router.get("/chained-calls")
async def chained_calls() -> dict:
    calls = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        calls.append(await _call_external(client, f"{HTTPBIN_BASE}/get"))
        calls.append(await _call_external(client, f"{HTTPBIN_BASE}/delay/1"))
    return {
        "status": "ok",
        "message": "chained calls completed",
        "calls": calls,
    }


@router.get("/parallel-calls")
async def parallel_calls() -> dict:
    start = time.time()
    async with httpx.AsyncClient(timeout=10.0) as client:
        results = await asyncio.gather(
            _call_external(client, f"{HTTPBIN_BASE}/get"),
            _call_external(client, f"{HTTPBIN_BASE}/get"),
        )
    total_elapsed_ms = int((time.time() - start) * 1000)
    return {
        "status": "ok",
        "message": "parallel calls completed",
        "total_elapsed_ms": total_elapsed_ms,
        "calls": [{"url": r["url"], "status": r["status"]} for r in results],
    }
