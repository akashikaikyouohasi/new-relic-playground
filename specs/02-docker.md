# 02: Docker 構成仕様

## 概要

アプリケーションを Docker コンテナで実行するための構成を定義する。Docker Compose を使用してサービスの管理を行う。

## ファイル構成

```
Dockerfile
docker-compose.yml
.env.example
.dockerignore
.gitignore
```

## Dockerfile

### 仕様

- **ベースイメージ**: `python:3.12-slim`
- **作業ディレクトリ**: `/app`
- **依存関係インストール**: `requirements.txt` から pip install
- **起動コマンド**: `newrelic-admin run-program uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 実装ガイド

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["newrelic-admin", "run-program", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## docker-compose.yml

### 仕様

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - NEW_RELIC_CONFIG_FILE=newrelic.ini
    volumes:
      - .:/app
    restart: unless-stopped
```

### 設計判断

- `volumes` でソースコードをマウントし、開発時の変更を即座に反映可能にする
- `env_file` で `.env` を読み込み、シークレットをコード外で管理
- `restart: unless-stopped` で意図しない停止からの自動復旧

## .env.example

環境変数のテンプレート。実際の値は `.env` に記載する。

```bash
# New Relic
NEW_RELIC_LICENSE_KEY=your_license_key_here
NEW_RELIC_APP_NAME=new-relic-playground
NEW_RELIC_LOG_LEVEL=info

# App
DEBUG=false
```

## .dockerignore

```
.git
.gitignore
.env
__pycache__
*.pyc
.pytest_cache
.ruff_cache
```

## .gitignore

```
# Environment
.env

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.ruff_cache/

# IDE
.vscode/
.idea/

# New Relic
newrelic-python-agent.log
```

## 検証手順

1. `.env.example` をコピーして `.env` を作成し、ライセンスキーを設定
2. `docker compose build` でイメージをビルド
3. `docker compose up` でコンテナを起動
4. `curl http://localhost:8000/health` で動作確認
5. `docker compose logs app` でログにエラーがないことを確認

## 受け入れ基準

- [ ] `docker compose build` がエラーなく完了する
- [ ] `docker compose up` でコンテナが起動する
- [ ] `http://localhost:8000/health` にアクセスできる
- [ ] `.env` ファイルが `.gitignore` に含まれている
- [ ] `.env.example` がリポジトリに含まれている
