# 01: アプリケーション構成仕様

## 概要

FastAPI を使用した Web アプリケーションの基本構成を定義する。このアプリケーションが New Relic の各機能を検証するための土台となる。

## アプリケーション構成

### ディレクトリ構造

```
app/
├── __init__.py
├── main.py              # FastAPI アプリ初期化
├── config.py            # 設定管理
├── routers/
│   ├── __init__.py
│   └── health.py        # ヘルスチェック
├── services/
│   └── __init__.py
└── utils/
    └── __init__.py

pyproject.toml           # パッケージ定義・依存管理（uv）
```

### 依存パッケージ（pyproject.toml）

`pyproject.toml` の `[project] dependencies` で管理する。パッケージマネージャには uv を使用する。

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
newrelic>=10.0.0
httpx>=0.27.0
pydantic-settings>=2.0.0
```

## 検証用エンドポイント

### GET /health

ヘルスチェック用エンドポイント。アプリケーションが正常に動作していることを確認する。

- **パス**: `/health`
- **メソッド**: GET
- **レスポンス**:
  ```json
  {
    "status": "ok",
    "app_name": "new-relic-playground",
    "version": "0.1.0"
  }
  ```

### GET /

ルートエンドポイント。API の概要情報を返す。

- **パス**: `/`
- **メソッド**: GET
- **レスポンス**:
  ```json
  {
    "app": "new-relic-playground",
    "docs": "/docs",
    "health": "/health"
  }
  ```

## 実装ガイド

### main.py

```python
from fastapi import FastAPI

from app.routers import health

app = FastAPI(
    title="New Relic Playground",
    version="0.1.0",
)

app.include_router(health.router)

@app.get("/")
async def root() -> dict[str, str]:
    return {
        "app": "new-relic-playground",
        "docs": "/docs",
        "health": "/health",
    }
```

### config.py

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "new-relic-playground"
    app_version: str = "0.1.0"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

### routers/health.py

```python
from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }
```

## 検証手順

1. アプリケーションを起動する
2. `curl http://localhost:8000/health` でヘルスチェックが返ることを確認
3. `curl http://localhost:8000/` でルートエンドポイントが返ることを確認
4. `http://localhost:8000/docs` で OpenAPI ドキュメントが表示されることを確認

## 受け入れ基準

- [ ] FastAPI アプリケーションが起動する
- [ ] `GET /health` が `{"status": "ok", ...}` を返す
- [ ] `GET /` が API 概要情報を返す
- [ ] `GET /docs` で OpenAPI ドキュメントが表示される
- [ ] `pyproject.toml` に必要なパッケージが定義されている
