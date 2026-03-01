# 構成図ルール

## 概要

プロジェクトの全体構成を draw.io 形式の構成図で管理する。

## ファイル

- `docs/architecture.drawio` — プロジェクト全体の構成図

## 構成図の要素

### 内部コンポーネント（Docker コンテナ内）

- FastAPI アプリケーション（各ルーター含む）
- New Relic Python Agent（計装レイヤー）
- uvicorn（ASGI サーバー）

### 外部コンポーネント

- Client（User/curl）
- 外部 API（httpbin.org 等）
- New Relic One（one.newrelic.com）

### データフロー

- 通信プロトコル（HTTP/HTTPS）をラベルに含める
- データ種別（APM, Spans, Errors, Logs, Custom Events/Metrics）を明記する

## 更新タイミング

- specs/ 配下の仕様書を新規追加したとき
- 既存の仕様書を変更し、コンポーネントやデータフローに影響があるとき
- 具体的には以下の変更時:
  - ルーター（エンドポイント）の追加・削除
  - 外部サービスとの通信の追加・削除
  - インフラ構成の変更（コンテナ追加等）

## 作図ツール

- draw.io（`.drawio` 形式）
- MCP サーバー `@drawio/mcp` を使って作成・更新する
