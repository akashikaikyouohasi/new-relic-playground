# 開発プロセス・ワークフロー

## 仕様駆動開発フロー

本プロジェクトでは、仕様書（specs/）を起点とした開発フローを採用する。

```
1. 仕様確認    → specs/ の該当仕様書を読み、検証内容を理解する
2. 実装        → 仕様に定義されたエンドポイント・ロジックを実装する
3. Docker 起動 → docker compose up --build で変更を反映
4. 動作確認    → curl やブラウザでエンドポイントにリクエストを送信
5. NR UI 確認  → New Relic One で計装データが正しく送信されていることを確認
6. チェックリスト更新 → specs/10-verification-checklist.md の該当項目をチェック
```

### 実装順序

仕様は番号順に依存関係がある。基盤仕様（01〜03）を先に実装し、その上に機能検証仕様（04〜09）を積み上げる。

1. **01-app-structure** → **02-docker** → **03-newrelic-agent-setup**（基盤。この順に実装）
2. **04-apm-basic**, **07-error-tracking**（必須。基盤完了後に実装）
3. **05, 06, 08, 09**（推奨。任意の順序で実装可能）

## 環境構築手順

### 初回セットアップ

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd new-relic-playground

# 2. 開発ツールのセットアップ（pre-commit フックの登録）
make setup

# 3. .env ファイルを作成
cp .env.example .env

# 4. .env に New Relic ライセンスキーを設定
# NEW_RELIC_LICENSE_KEY=your_license_key_here

# 5. Docker Compose で起動
docker compose up --build
```

### 日常の開発サイクル

```bash
# コード変更後にコンテナを再ビルド・起動
docker compose up --build

# バックグラウンドで起動
docker compose up --build -d

# ログを確認
docker compose logs -f app

# コンテナを停止
docker compose down
```

## よく使う Docker コマンド

```bash
# コンテナの状態確認
docker compose ps

# アプリコンテナに入る
docker compose exec app bash

# コンテナを再ビルド（キャッシュなし）
docker compose build --no-cache

# ボリュームも含めて完全に削除
docker compose down -v

# 特定のサービスだけ再起動
docker compose restart app
```

## New Relic UI での確認方法

### APM の確認

1. [New Relic One](https://one.newrelic.com) にログイン
2. 左メニューから **APM & Services** を選択
3. アプリケーション名（`new-relic-playground`）を選択
4. **Summary** でトランザクション、レスポンスタイム、スループットを確認

### NRQL クエリの実行方法

1. New Relic One の左メニューから **Query Your Data** を選択
2. NRQL クエリを入力して実行

```sql
-- 直近30分のトランザクション一覧
SELECT * FROM Transaction WHERE appName = 'new-relic-playground' SINCE 30 minutes ago

-- エラー一覧
SELECT * FROM TransactionError WHERE appName = 'new-relic-playground' SINCE 1 hour ago

-- カスタムイベント
SELECT * FROM CustomEvent WHERE appName = 'new-relic-playground' SINCE 1 hour ago
```

### Logs の確認

1. 左メニューから **Logs** を選択
2. フィルターで `service.name = 'new-relic-playground'` を設定
3. ログに `trace.id` が含まれていることを確認（Logs in Context）

## トラブルシューティング

### New Relic にデータが表示されない

1. **ライセンスキーの確認**: `.env` の `NEW_RELIC_LICENSE_KEY` が正しいか確認
2. **エージェントログの確認**: コンテナ内の `/tmp/newrelic-python-agent.log` を確認
   ```bash
   docker compose exec app cat /tmp/newrelic-python-agent.log
   ```
3. **ネットワーク確認**: コンテナから New Relic のコレクターエンドポイントにアクセスできるか確認
4. **データ遅延**: New Relic UI への反映には数分かかる場合がある。2〜3 分待ってからリロード

### Docker 関連のトラブル

1. **ポートの競合**: `docker compose ps` で使用中のポートを確認し、`docker-compose.yml` で変更
2. **ビルドエラー**: `docker compose build --no-cache` でキャッシュなしリビルド
3. **コンテナが起動しない**: `docker compose logs app` でエラーログを確認

### Python 依存関係のトラブル

1. **パッケージが見つからない**: `requirements.txt` に追加して `docker compose build` を再実行
2. **バージョン競合**: `pip install` のエラーメッセージで競合パッケージを特定し、バージョンを調整

## コミット規約

### pre-commit による自動チェック

`make setup` を実行すると `pre-commit` フックが登録される。
`git commit` 実行時に以下のチェックが自動で走る:

- **ruff**: リントエラーがないかチェック
- **ruff-format**: フォーマットが正しいかチェック

チェックに失敗した場合はコミットがブロックされる。エラーを修正してから再度コミットすること。

### `/commit` コマンドの使い方

Claude Code の `/commit` コマンドを使うと、ステージ済みの変更を元に適切なコミットメッセージを自動生成してコミットできる。

```bash
# 変更をステージ
git add <files>

# Claude Code でコミット（コミットメッセージを自動生成）
/commit
```

コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/) 形式（`feat:`, `fix:`, `docs:` など）を使用すること。
