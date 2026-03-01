.PHONY: setup lint format test up down logs smoke help

help: ## 利用可能なコマンドを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## 開発環境のセットアップ
	uv sync
	uv run pre-commit install

lint: ## ruff で lint を実行
	uv run ruff check .

format: ## ruff で format を実行
	uv run ruff format .

test: ## pytest でテストを実行
	uv run pytest -v

up: ## Docker Compose でアプリを起動
	docker compose up --build -d

down: ## Docker Compose でアプリを停止
	docker compose down

logs: ## Docker Compose のログを表示
	docker compose logs -f app

smoke: ## 対話的にエンドポイントをテスト
	bash scripts/smoke_test.sh
