以下の手順でコミットを作成してください：

1. `git status` と `git diff` で変更内容を確認する
2. 関連ファイルを `git add` する（`.env` などの機密ファイルは除外する）
3. コミットメッセージは `<prefix>: <一行のメッセージ>` の形式で作成する
   - prefix は Conventional Commits に従う（`feat`, `fix`, `docs`, `chore`, `refactor`, `test` など）
   - メッセージは日本語OK、簡潔に変更内容を表す一文にする
   - 例: `feat: ユーザー認証エンドポイントを追加`
   - **メッセージは必ず1行で完結させること（改行を含めない）**
   - **`Co-Authored-By` などの trailer は付けない**
4. `git commit -m "メッセージ"` する（改行なしの `-m` 形式を使うこと）
5. `git push` する
6. `git status` でコミット・プッシュ成功を確認する
