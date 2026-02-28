import time

import newrelic.agent
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/custom-instrumentation", tags=["custom-instrumentation"]
)


class BackgroundTaskRequest(BaseModel):
    task_name: str
    items: int


@newrelic.agent.function_trace(name="step_a")
def step_a() -> str:
    time.sleep(0.1)
    return "step_a: 100ms"


@newrelic.agent.function_trace(name="step_b")
def step_b() -> str:
    time.sleep(0.2)
    return "step_b: 200ms"


@newrelic.agent.function_trace(name="step_c")
def step_c() -> str:
    time.sleep(0.05)
    return "step_c: 50ms"


@router.get("/function-trace")
async def function_trace_endpoint() -> dict:
    steps = [step_a(), step_b(), step_c()]
    return {
        "status": "ok",
        "message": "function trace demo",
        "steps": steps,
    }


@newrelic.agent.background_task(name="data_processing")
def _process_data(items: int) -> None:
    for _ in range(items):
        time.sleep(0.01)


@router.post("/background-task")
async def background_task_endpoint(body: BackgroundTaskRequest) -> dict:
    _process_data(body.items)
    return {
        "status": "ok",
        "message": "background task started",
        "task_name": body.task_name,
    }


@router.get("/custom-attributes")
async def custom_attributes_endpoint() -> dict:
    attributes = {
        "user_tier": "premium",
        "feature_flag": "new_dashboard",
        "request_priority": "high",
    }
    newrelic.agent.add_custom_attributes(list(attributes.items()))
    return {
        "status": "ok",
        "message": "custom attributes added",
        "attributes": attributes,
    }
