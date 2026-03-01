# 03: New Relic エージェント設定仕様

## 概要

New Relic Python Agent をアプリケーションに導入し、基本的なデータ送信が行われることを確認する。この仕様が完了すると、New Relic One の APM 画面にアプリケーションが表示される。

## 設定ファイル

### newrelic.ini

```ini
[newrelic]
# アプリケーション名（New Relic UI に表示される名前）
app_name = new-relic-playground

# ライセンスキーは環境変数 NEW_RELIC_LICENSE_KEY から自動取得される

# 分散トレーシングを有効化
distributed_tracing.enabled = true

# ログ転送を有効化（Logs in Context 用）
application_logging.enabled = true
application_logging.forwarding.enabled = true
application_logging.metrics.enabled = true
application_logging.local_decorating.enabled = false

# エージェントログ設定
log_file = /tmp/newrelic-python-agent.log
log_level = info

# トランザクショントレーサー
transaction_tracer.enabled = true
transaction_tracer.transaction_threshold = apdex_f

# エラーコレクター
error_collector.enabled = true

# ブラウザモニタリング（サーバーサイド API のため無効）
browser_monitoring.auto_instrument = false
```

### 設定の優先順位

New Relic Agent の設定は以下の優先順位で適用される:

1. サーバーサイド設定（New Relic UI から設定）
2. 環境変数（`NEW_RELIC_*`）
3. `newrelic.ini` の値

## 起動方法

### Docker 内での起動

`Dockerfile` の CMD で `newrelic-admin` を使用:

```dockerfile
CMD ["newrelic-admin", "run-program", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 環境変数

```bash
# 必須
NEW_RELIC_CONFIG_FILE=newrelic.ini
NEW_RELIC_LICENSE_KEY=<your-license-key>

# オプション（newrelic.ini の値をオーバーライド）
NEW_RELIC_APP_NAME=new-relic-playground
NEW_RELIC_LOG_LEVEL=info
```

## 検証手順

1. Docker Compose でアプリケーションを起動
   ```bash
   docker compose up --build
   ```

2. ヘルスチェックエンドポイントにリクエストを送信（トランザクションを生成）
   ```bash
   curl http://localhost:8000/health
   ```

3. エージェントログを確認
   ```bash
   docker compose exec app cat /tmp/newrelic-python-agent.log
   ```
   - 「Reporting to」メッセージが表示されていれば接続成功

4. New Relic One で確認
   - APM & Services にアプリケーション `new-relic-playground` が表示されること
   - Summary 画面にトランザクションデータが表示されること

## NRQL クエリ

```sql
-- アプリケーションが登録されているか確認
SELECT count(*) FROM Transaction WHERE appName = 'new-relic-playground' SINCE 10 minutes ago

-- エージェントバージョンの確認
SELECT latest(nr.agentVersion) FROM Transaction WHERE appName = 'new-relic-playground' SINCE 1 hour ago
```

## 受け入れ基準

- [ ] `newrelic.ini` が正しい設定で作成されている
- [ ] `newrelic-admin run-program` でアプリケーションが起動する
- [ ] エージェントログに「Reporting to」メッセージが出力される
- [ ] New Relic One の APM にアプリケーションが表示される
- [ ] ヘルスチェックのトランザクションが New Relic に記録される
- [ ] ライセンスキーがソースコードにハードコードされていない
