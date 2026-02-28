import logging

from fastapi import FastAPI

from app.routers import apm, custom, custom_events, errors, health, logs, tracing

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="New Relic Playground",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(apm.router)
app.include_router(errors.router)
app.include_router(custom.router)
app.include_router(tracing.router)
app.include_router(logs.router)
app.include_router(custom_events.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "app": "new-relic-playground",
        "docs": "/docs",
        "health": "/health",
    }
