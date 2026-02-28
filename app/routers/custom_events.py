import random

import newrelic.agent
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/custom", tags=["custom-events"])


class CustomEventRequest(BaseModel):
    event_type: str
    attributes: dict


class CustomMetricRequest(BaseModel):
    metric_name: str
    value: float


class BatchEventRequest(BaseModel):
    event_type: str
    count: int


@router.post("/event")
async def record_event(body: CustomEventRequest) -> dict:
    newrelic.agent.record_custom_event(body.event_type, body.attributes)
    return {
        "status": "ok",
        "message": "custom event recorded",
        "event_type": body.event_type,
    }


@router.post("/metric")
async def record_metric(body: CustomMetricRequest) -> dict:
    newrelic.agent.record_custom_metric(body.metric_name, body.value)
    return {
        "status": "ok",
        "message": "custom metric recorded",
        "metric_name": body.metric_name,
        "value": body.value,
    }


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
