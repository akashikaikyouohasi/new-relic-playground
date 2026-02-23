# コーディング規約

## Python コーディング規約

### 基本方針

- PEP 8 に準拠する
- フォーマッターとして **ruff** を使用する
- 最大行長: 120 文字

### 型ヒント

型ヒントを必須とする。すべての関数の引数と戻り値に型アノテーションを付与する。

```python
# Good
def get_user(user_id: int) -> dict[str, Any]:
    ...

# Bad
def get_user(user_id):
    ...
```

### import 順序

以下の順序で記述し、各グループ間は空行で区切る:

1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルモジュール

```python
import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
import newrelic.agent

from app.services.user_service import UserService
from app.config import settings
```

### 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| 変数・関数 | snake_case | `user_name`, `get_user()` |
| クラス | PascalCase | `UserService` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| ファイル名 | snake_case | `user_service.py` |
| エンドポイントパス | kebab-case | `/api/custom-events` |

## FastAPI エンドポイントの書き方

### Router の定義

各機能ごとに Router を分割し、`app/routers/` に配置する。

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/apm", tags=["apm"])

@router.get("/slow")
async def slow_endpoint() -> dict[str, str]:
    """意図的に遅いレスポンスを返すエンドポイント（APM 検証用）"""
    await asyncio.sleep(2)
    return {"status": "ok", "message": "slow response"}
```

### レスポンス形式

すべてのエンドポイントは JSON を返す。共通のレスポンス構造:

```python
{
    "status": "ok" | "error",
    "message": "説明文",
    "data": { ... }  # オプション
}
```

### エラーレスポンス

HTTPException を使用する:

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="User not found")
```

## ロギング規約

### 基本方針

- Python 標準の `logging` モジュールを使用する
- `print()` は使用しない（デバッグ目的でも `logger.debug()` を使う）
- New Relic Logs in Context との連携のため、構造化ログを出力する

### ロガーの定義

各モジュールの先頭でロガーを定義する:

```python
import logging

logger = logging.getLogger(__name__)
```

### ログレベルの使い分け

| レベル | 用途 |
|--------|------|
| `DEBUG` | 開発時のデバッグ情報 |
| `INFO` | 正常な処理の記録（リクエスト受信、処理完了等） |
| `WARNING` | 想定内の異常（リトライ、フォールバック等） |
| `ERROR` | 処理失敗（例外発生、外部 API エラー等） |
| `CRITICAL` | システム停止レベルの障害 |

### ログ出力の例

```python
logger.info("Processing request", extra={"user_id": user_id, "action": "get_profile"})
logger.error("External API call failed", extra={"url": url, "status_code": response.status_code})
```

## エラーハンドリング規約

### 基本方針

- 予期されるエラーは適切にキャッチし、意味のあるエラーレスポンスを返す
- 予期しないエラーは FastAPI のデフォルトハンドラーに任せる（New Relic が自動キャプチャ）
- bare `except:` は使用しない（最低でも `except Exception:` とする）

### New Relic へのエラー通知

自動キャプチャされない場合や追加情報を付与したい場合:

```python
import newrelic.agent

try:
    result = some_operation()
except SomeException as e:
    newrelic.agent.notice_error(attributes={"operation": "some_operation", "detail": str(e)})
    raise
```

## プロジェクト固有のルール

### ファイル構成

- 1 ファイルは 1 つの責務に限定する
- Router ファイルにビジネスロジックを書かない（Services 層に分離）
- ユーティリティ関数は `app/utils/` に配置する

### New Relic 計装コード

- 自動計装で十分な場合はカスタムコードを追加しない
- カスタム計装を追加する場合は、仕様書（specs/）に定義されたパターンに従う
- カスタムアトリビュートやイベントの命名は仕様書に従う
