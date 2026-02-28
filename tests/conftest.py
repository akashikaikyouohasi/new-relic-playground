import os

import pytest
from fastapi.testclient import TestClient

os.environ["NEW_RELIC_ENABLED"] = "false"


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    return TestClient(app)
