# 🚀 本番環境デプロイ手順（ステップバイステップ）

## 📋 ステップ1: 変更をGitHubにプッシュ

### 1-1. 変更を確認

```bash
cd /Users/okazakikatsuhiro/Replit-ConnectPlus
git status
```

### 1-2. すべての変更をステージング

```bash
git add .
```

### 1-3. コミット

```bash
git commit -m "本番環境デプロイ準備: パスワード表示機能追加、設定ファイル追加"
```

### 1-4. GitHubにプッシュ

```bash
git push origin main
```

---

## 🚂 ステップ2: Railwayでデプロイ（推奨）

### 2-1. Railwayアカウントの作成

1. ブラウザで https://railway.app にアクセス
2. 「Start a New Project」をクリック
3. 「Login with GitHub」をクリック
4. GitHubアカウントで認証

### 2-2. プロジェクトの作成

1. Railwayダッシュボードで「New Project」をクリック
2. 「Deploy from GitHub repo」を選択
3. リポジトリ一覧から `yasuoka0219/Replit-ConnectPlus` を選択
4. 「Deploy Now」をクリック

### 2-3. PostgreSQLデータベースの追加

1. Railwayダッシュボードで「New」ボタンをクリック
2. 「Database」を選択
3. 「Add PostgreSQL」をクリック
4. 自動的に `DATABASE_URL` 環境変数が設定されます

### 2-4. 環境変数の設定

1. Railwayダッシュボードで「Variables」タブをクリック
2. 以下の環境変数を追加：

**SESSION_SECRET の生成：**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**環境変数の追加：**
- `SESSION_SECRET`: 上記コマンドで生成した文字列をコピー&ペースト
- `FLASK_DEBUG`: `False` と入力

### 2-5. デプロイの確認

1. Railwayダッシュボードの「Deployments」タブでデプロイの進行状況を確認
2. デプロイが完了すると「Active」と表示されます
3. 「Settings」タブで「Generate Domain」をクリックしてURLを取得

### 2-6. データベースの初期化

1. Railway CLIをインストール（初回のみ）:
```bash
npm i -g @railway/cli
```

2. Railwayにログイン:
```bash
railway login
```

3. プロジェクトに接続:
```bash
cd /Users/okazakikatsuhiro/Replit-ConnectPlus
railway link
# プロジェクトを選択
```

4. データベースマイグレーションを実行:
```bash
railway run python migrate_db.py
```

### 2-7. 動作確認

1. Railwayダッシュボードの「Settings」タブで取得したURLにアクセス
2. ログインページが表示されることを確認
3. 新規登録ができることを確認

---

## 🌐 ステップ3: Renderでデプロイ（代替案）

### 3-1. Renderアカウントの作成

1. ブラウザで https://render.com にアクセス
2. 「Get Started for Free」をクリック
3. 「Sign up with GitHub」をクリック
4. GitHubアカウントで認証

### 3-2. Webサービスの作成

1. Renderダッシュボードで「New +」をクリック
2. 「Web Service」を選択
3. 「Connect account」でGitHubアカウントを接続（初回のみ）
4. リポジトリ一覧から `yasuoka0219/Replit-ConnectPlus` を選択
5. 「Connect」をクリック

### 3-3. サービスの設定

以下の設定を入力：

- **Name**: `connectplus`（任意）
- **Environment**: `Python 3`
- **Region**: `Oregon (US West)`（最寄りのリージョンを選択）
- **Branch**: `main`
- **Root Directory**: （空白のまま）
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 3-4. PostgreSQLデータベースの追加

1. Renderダッシュボードで「New +」をクリック
2. 「PostgreSQL」を選択
3. 以下の設定を入力：
   - **Name**: `connectplus-db`
   - **Database**: `connectplus`
   - **User**: （自動生成）
   - **Region**: Webサービスと同じリージョン
   - **Plan**: `Free`（または有料プラン）
4. 「Create Database」をクリック

### 3-5. 環境変数の設定

1. Webサービスの「Environment」タブを開く
2. 「Add Environment Variable」をクリック
3. 以下の環境変数を追加：

**SESSION_SECRET の生成：**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**環境変数の追加：**
- `SESSION_SECRET`: 上記コマンドで生成した文字列
- `FLASK_DEBUG`: `False`
- `DATABASE_URL`: PostgreSQLデータベースの「Internal Database URL」をコピー&ペースト

### 3-6. デプロイの確認

1. 「Create Web Service」をクリック
2. デプロイの進行状況を確認
3. デプロイが完了すると「Live」と表示されます

### 3-7. データベースの初期化

1. RenderダッシュボードでWebサービスを開く
2. 「Shell」タブをクリック
3. 以下のコマンドを実行：
```bash
python migrate_db.py
```

### 3-8. 動作確認

1. RenderダッシュボードのWebサービスページでURLを確認
2. そのURLにアクセス
3. ログインページが表示されることを確認

---

## 🔄 ステップ4: 継続的な開発フロー

### 4-1. ローカルで開発

```bash
cd /Users/okazakikatsuhiro/Replit-ConnectPlus
PORT=5001 python3 app.py
```

`http://localhost:5001` で動作確認

### 4-2. 変更をコミット

```bash
git add .
git commit -m "機能名: 変更内容の説明"
git push origin main
```

### 4-3. 自動デプロイ

- Railway/Renderが自動的にGitHubの変更を検知
- 自動的にビルド・デプロイが開始されます
- デプロイの進行状況はダッシュボードで確認できます

### 4-4. データベースマイグレーション（必要に応じて）

**Railway:**
```bash
railway run python migrate_db.py
```

**Render:**
- Shellから実行: `python migrate_db.py`

---

## ✅ デプロイ後の確認事項

- [ ] アプリケーションが起動している
- [ ] ログインページが表示される
- [ ] 新規登録ができる
- [ ] ダッシュボードが表示される
- [ ] データベース接続が正常
- [ ] エラーログに問題がないか確認

---

## 🆘 トラブルシューティング

### デプロイが失敗する場合

1. **ログを確認**
   - Railway: 「Deployments」→「View Logs」
   - Render: 「Logs」タブ

2. **環境変数を確認**
   - `DATABASE_URL` が正しく設定されているか
   - `SESSION_SECRET` が設定されているか

3. **requirements.txtを確認**
   - すべての依存パッケージが含まれているか

### データベース接続エラー

1. `DATABASE_URL` 環境変数を確認
2. データベースが作成されているか確認
3. マイグレーションを再実行

---

## 📚 参考資料

- Railway公式ドキュメント: https://docs.railway.app
- Render公式ドキュメント: https://render.com/docs
- 詳細なワークフロー: `DEPLOYMENT_WORKFLOW.md` を参照

---

**質問や問題があれば、お気軽にお尋ねください！**

