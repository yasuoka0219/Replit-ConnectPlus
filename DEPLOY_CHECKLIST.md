# ✅ 本番環境デプロイチェックリスト

本番環境にデプロイする前に、以下の項目を確認してください。

## 🔒 セキュリティ設定

- [ ] `SESSION_SECRET` を強力なランダム文字列に設定
  ```bash
  # 生成コマンド
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] `FLASK_DEBUG=False` に設定（本番環境）
  - Railway/Renderの環境変数で `FLASK_DEBUG=False` を設定
  - または、`app.py`のデフォルトが`False`になっていることを確認

- [ ] データベースパスワードが強力であることを確認

- [ ] `.env`ファイルがGitに含まれていないことを確認（`.gitignore`に含まれているか）

## 📦 デプロイ前の確認

- [ ] すべての変更をコミット済み
  ```bash
  git status
  ```

- [ ] ローカルで動作確認済み
  ```bash
  PORT=5001 python3 app.py
  # http://localhost:5001 で動作確認
  ```

- [ ] `requirements.txt` に必要なパッケージがすべて含まれている

- [ ] `Procfile` が正しく設定されている（Heroku使用時）
  ```
  web: gunicorn app:app
  ```

- [ ] `railway.json` が存在する（Railway使用時）

- [ ] `render.yaml` が存在する（Render使用時）

## 🗄️ データベース

- [ ] 本番環境のデータベースが作成されている
- [ ] `DATABASE_URL` 環境変数が正しく設定されている
- [ ] データベースマイグレーションを実行する準備ができている
  ```bash
  # Railway
  railway run python migrate_db.py
  
  # Render
  # Shellから実行: python migrate_db.py
  ```

## 🚀 デプロイ手順

### Railwayの場合

1. [ ] Railwayアカウントを作成
2. [ ] GitHubリポジトリを接続
3. [ ] PostgreSQLデータベースを追加
4. [ ] 環境変数を設定：
   - `SESSION_SECRET`
   - `FLASK_DEBUG=False`
5. [ ] デプロイを確認
6. [ ] データベースマイグレーションを実行

### Renderの場合

1. [ ] Renderアカウントを作成
2. [ ] GitHubリポジトリを接続
3. [ ] Webサービスを作成
4. [ ] PostgreSQLデータベースを追加
5. [ ] 環境変数を設定：
   - `SESSION_SECRET`
   - `FLASK_DEBUG=False`
6. [ ] デプロイを確認
7. [ ] データベースマイグレーションを実行

## ✅ デプロイ後の確認

- [ ] アプリケーションが起動している
- [ ] ログインページが表示される
- [ ] 新規登録ができる
- [ ] ダッシュボードが表示される
- [ ] データベース接続が正常
- [ ] エラーログに問題がないか確認

## 🔄 継続開発の準備

- [ ] ローカル開発環境が整っている
- [ ] Gitの設定が完了している
- [ ] GitHubリポジトリが設定されている
- [ ] デプロイワークフローを理解している

---

## 📝 デプロイコマンド（参考）

### 初回デプロイ

```bash
# 1. 変更をコミット
git add .
git commit -m "本番環境デプロイ準備"

# 2. GitHubにプッシュ
git push origin main

# 3. Railway/Renderで自動デプロイが開始される
# 4. デプロイ完了後、データベースマイグレーションを実行
```

### データベースマイグレーション

```bash
# Railway
railway run python migrate_db.py

# Render（Shellから）
python migrate_db.py
```

---

**すべての項目を確認してからデプロイを開始してください！**

