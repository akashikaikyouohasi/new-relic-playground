# 仕様全体の概要

## 目的

本プロジェクトは、New Relic の主要機能を Python（FastAPI）アプリケーションで検証することを目的とする。各仕様書は検証対象の機能ごとに分割されており、番号順に実装することで段階的に検証環境を構築できる。

## 仕様書一覧

| 番号 | ファイル | 内容 | 優先度 | 依存 |
|------|----------|------|--------|------|
| 01 | [01-app-structure.md](01-app-structure.md) | アプリケーション構成仕様 | 必須 | なし |
| 02 | [02-docker.md](02-docker.md) | Docker 構成仕様 | 必須 | 01 |
| 03 | [03-newrelic-agent-setup.md](03-newrelic-agent-setup.md) | New Relic エージェント設定仕様 | 必須 | 01, 02 |
| 04 | [04-apm-basic.md](04-apm-basic.md) | APM 基本機能の検証仕様 | 必須 | 03 |
| 05 | [05-custom-instrumentation.md](05-custom-instrumentation.md) | カスタム計装の検証仕様 | 推奨 | 03 |
| 06 | [06-distributed-tracing.md](06-distributed-tracing.md) | 分散トレーシングの検証仕様 | 推奨 | 03 |
| 07 | [07-error-tracking.md](07-error-tracking.md) | エラートラッキングの検証仕様 | 必須 | 03 |
| 08 | [08-logs-in-context.md](08-logs-in-context.md) | Logs in Context の検証仕様 | 推奨 | 03 |
| 09 | [09-custom-events-metrics.md](09-custom-events-metrics.md) | カスタムイベント・メトリクスの検証仕様 | 推奨 | 03 |
| 10 | [10-verification-checklist.md](10-verification-checklist.md) | 総合検証チェックリスト | - | 全仕様 |
| 11 | [11-architecture-diagram.md](11-architecture-diagram.md) | 構成図 | 推奨 | 全仕様 |

## 実装順序と依存関係

```
01-app-structure ──▶ 02-docker ──▶ 03-newrelic-agent-setup ──┬──▶ 04-apm-basic
                                                               ├──▶ 05-custom-instrumentation
                                                               ├──▶ 06-distributed-tracing
                                                               ├──▶ 07-error-tracking
                                                               ├──▶ 08-logs-in-context
                                                               └──▶ 09-custom-events-metrics
```

- **01〜03（基盤）**: 順番に実装する必要がある。アプリの骨格 → Docker 化 → New Relic Agent 導入
- **04〜09（機能検証）**: 基盤（03）完了後は任意の順序で実装可能。ただし、必須（04, 07）を優先推奨
- **10（チェックリスト）**: 全仕様の検証結果を集約。各仕様の実装完了時に随時更新

## 前提条件

### 必須

- New Relic アカウント（Free tier で可）
- New Relic ライセンスキー（Ingest - License タイプ）
- Docker / Docker Compose がインストールされた環境
- Python 3.12+ の基本的な知識

### 推奨

- FastAPI の基本的な知識
- New Relic One UI の操作経験
- NRQL（New Relic Query Language）の基本知識

## 仕様書の統一フォーマット

各仕様書（01〜09）は以下の構成で記述されている:

1. **概要**: 検証対象の機能説明
2. **検証用エンドポイント**: 実装すべき API の一覧と仕様
3. **実装ガイド**: コード例と設定方法
4. **検証手順**: New Relic UI での確認手順
5. **NRQL クエリ**: データ検証用のクエリ
6. **受け入れ基準**: チェックリスト形式の完了条件
