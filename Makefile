.PHONY: setup lint format help

help: ## 利用可能なコマンドを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## 開発環境のセットアップ（pre-commit の登録）
	pip install pre-commit
	pre-commit install

lint: ## ruff で lint を実行
	ruff check .

format: ## ruff で format を実行
	ruff format .
