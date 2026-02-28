import logging

import newrelic.agent
from fastapi import APIRouter

router = APIRouter(prefix="/api/logs", tags=["logs"])

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


@router.get("/structured")
async def structured_logs() -> dict:
    attributes = {
        "user_id": "user-123",
        "action": "profile_view",
        "duration_ms": 45,
    }
    logger.info(
        "User action recorded",
        extra=attributes,
    )
    return {
        "status": "ok",
        "message": "structured logs emitted",
        "attributes": attributes,
    }


@router.get("/with-error")
async def logs_with_error() -> dict:
    try:
        raise ValueError("Something went wrong during processing")
    except ValueError:
        logger.exception("An error occurred during processing")
        newrelic.agent.notice_error()
    return {
        "status": "ok",
        "message": "error logged and reported",
        "trace_context": "check New Relic for trace.id correlation",
    }
