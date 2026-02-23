.PHONY: setup lint format help

help: ## 利用可能なコマンドを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## 開発環境のセットアップ
	uv sync
	uv run pre-commit install

lint: ## ruff で lint を実行
	uv run ruff check .

format: ## ruff で format を実行
	uv run ruff format .
