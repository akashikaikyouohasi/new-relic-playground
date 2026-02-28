import newrelic.agent
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/errors", tags=["errors"])


class CustomErrorRequest(BaseModel):
    error_message: str
    user_id: str
    order_id: str


@router.get("/unhandled")
async def unhandled_error() -> dict:
    raise RuntimeError("This is an unhandled error for testing")


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


@router.get("/http-error")
async def http_error(
    status_code: int = Query(default=500, ge=400, le=599),
) -> dict:
    raise HTTPException(
        status_code=status_code,
        detail=f"Simulated error with status {status_code}",
    )


@router.post("/custom-error")
async def custom_error(body: CustomErrorRequest) -> dict:
    try:
        raise Exception(body.error_message)  # noqa: TRY002
    except Exception:
        newrelic.agent.notice_error(
            attributes={
                "user_id": body.user_id,
                "order_id": body.order_id,
            }
        )
    return {
        "status": "ok",
        "message": "custom error reported to New Relic",
        "attributes": {"user_id": body.user_id, "order_id": body.order_id},
    }
