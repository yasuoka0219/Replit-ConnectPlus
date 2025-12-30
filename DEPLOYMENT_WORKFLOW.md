# 🚀 本番環境デプロイ & 継続開発ワークフロー

CONNECT+ CRMを本番環境にデプロイし、Cursorで継続的に調整を加えていくための推奨ワークフローです。

## 📋 推奨デプロイ方法

### Railway（推奨）または Render

**理由：**
- GitHubと自動連携で簡単デプロイ
- 無料プランあり（Railwayは$5クレジット/月、Renderは無料プランあり）
- 自動ビルド・デプロイ
- 環境変数の管理が簡単
- データベース（PostgreSQL）の自動セットアップ

---

## 🔄 継続開発のワークフロー

### 基本フロー

```
1. ローカルで開発・テスト
   ↓
2. Gitでコミット
   ↓
3. GitHubにプッシュ
   ↓
4. 自動デプロイ（Railway/Render）
   ↓
5. 本番環境で動作確認
```

---

## 📝 ステップバイステップガイド

### ステップ1: 現在の変更をコミット

```bash
cd /Users/okazakikatsuhiro/Replit-ConnectPlus

# 変更を確認
git status

# 変更をステージング
git add app.py templates/register.html templates/settings_2fa.html

# コミット
git commit -m "パスワード表示/非表示機能を追加"

# GitHubにプッシュ
git push origin main
```

### ステップ2: Railwayでデプロイ（推奨）

#### 2-1. Railwayアカウントの作成

1. https://railway.app にアクセス
2. GitHubアカウントでサインアップ

#### 2-2. プロジェクトの作成

1. Railwayダッシュボードで "New Project" をクリック
2. "Deploy from GitHub repo" を選択
3. `yasuoka0219/Replit-ConnectPlus` リポジトリを選択

#### 2-3. PostgreSQLデータベースの追加

1. Railwayダッシュボードで "New" → "Database" → "Add PostgreSQL" を選択
2. 自動的に `DATABASE_URL` 環境変数が設定されます

#### 2-4. 環境変数の設定

Railwayダッシュボードの "Variables" タブで以下を設定：

```bash
SESSION_SECRET=<強力なランダム文字列>
```

**SESSION_SECRETの生成方法：**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 2-5. ビルド設定の確認

Railwayは自動的にPythonアプリを検出しますが、必要に応じて `railway.json` を作成：

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2-6. データベースの初期化

Railway CLIを使用（またはRailwayダッシュボードのShellから）：

```bash
# Railway CLIのインストール（初回のみ）
npm i -g @railway/cli

# ログイン
railway login

# プロジェクトに接続
railway link

# データベースマイグレーション実行
railway run python migrate_db.py
```

### ステップ3: Renderでデプロイ（代替案）

#### 3-1. Renderアカウントの作成

1. https://render.com にアクセス
2. GitHubアカウントでサインアップ

#### 3-2. Webサービスの作成

1. "New" → "Web Service" を選択
2. GitHubリポジトリを接続
3. 以下の設定を入力：
   - **Name**: `connectplus`（任意）
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

#### 3-3. PostgreSQLデータベースの追加

1. "New" → "PostgreSQL" を選択
2. 自動的に `DATABASE_URL` 環境変数が設定されます

#### 3-4. 環境変数の設定

Renderダッシュボードの "Environment" タブで：

```bash
SESSION_SECRET=<強力なランダム文字列>
```

#### 3-5. データベースの初期化

Renderダッシュボードの "Shell" から：

```bash
python migrate_db.py
```

---

## 🔄 継続的な開発・更新のワークフロー

### 日常的な開発サイクル

#### 1. ローカルで開発

```bash
# ローカルサーバーを起動
cd /Users/okazakikatsuhiro/Replit-ConnectPlus
PORT=5001 python3 app.py
```

- `http://localhost:5001` で動作確認
- Cursorでコードを編集
- ブラウザで動作確認

#### 2. 変更をコミット

```bash
# 変更を確認
git status

# 変更をステージング
git add .

# コミット（意味のあるメッセージを付ける）
git commit -m "機能名: 変更内容の説明"

# 例：
# git commit -m "パスワード表示機能: 登録ページに追加"
# git commit -m "UI改善: ダッシュボードのグラフを更新"
```

#### 3. GitHubにプッシュ

```bash
git push origin main
```

#### 4. 自動デプロイ

- **Railway/Render**: GitHubにプッシュすると自動的にデプロイが開始されます
- デプロイの進行状況はダッシュボードで確認できます

#### 5. 本番環境で動作確認

- デプロイ完了後、本番URLで動作確認
- 問題があればログを確認

---

## 🛠️ データベースマイグレーション

### スキーマ変更時の手順

1. **ローカルでマイグレーションスクリプトを作成・実行**

```bash
# 新しいマイグレーションスクリプトを作成（必要に応じて）
# または既存の migrate_db.py を更新

# ローカルでテスト
python migrate_db.py
```

2. **変更をコミット・プッシュ**

```bash
git add migrate_db.py
git commit -m "データベース: 新しいカラムを追加"
git push origin main
```

3. **本番環境でマイグレーション実行**

**Railwayの場合：**
```bash
railway run python migrate_db.py
```

**Renderの場合：**
- Renderダッシュボードの "Shell" から実行：
```bash
python migrate_db.py
```

---

## 🔒 セキュリティチェックリスト

本番環境デプロイ前に確認：

- [ ] `SESSION_SECRET` を強力なランダム文字列に設定
- [ ] `app.py` の `debug=False` に設定（本番環境）
- [ ] データベースパスワードが強力
- [ ] HTTPSが有効（Railway/Renderは自動）
- [ ] 環境変数に機密情報が含まれていないか確認

### app.pyのデバッグモード設定

本番環境では、`app.py` の最後の部分を確認：

```python
# 本番環境では debug=False に設定
debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
```

環境変数 `FLASK_DEBUG=False` を設定するか、デフォルトを `False` に変更してください。

---

## 📊 デプロイ後の確認事項

### 1. アプリケーションの動作確認

- [ ] ログインページが表示される
- [ ] 新規登録ができる
- [ ] ダッシュボードが表示される
- [ ] データベース接続が正常

### 2. ログの確認

**Railway:**
- ダッシュボードの "Deployments" → "View Logs"

**Render:**
- ダッシュボードの "Logs" タブ

### 3. エラーの監視

- デプロイログでエラーがないか確認
- アプリケーションログでエラーがないか確認

---

## 🔧 トラブルシューティング

### デプロイが失敗する場合

1. **ログを確認**
   - Railway/Renderのデプロイログを確認
   - エラーメッセージを確認

2. **環境変数を確認**
   - `DATABASE_URL` が正しく設定されているか
   - `SESSION_SECRET` が設定されているか

3. **requirements.txtを確認**
   - すべての依存パッケージが含まれているか

### データベース接続エラー

1. **DATABASE_URLを確認**
   - Railway/Renderの環境変数で確認
   - 接続文字列が正しいか確認

2. **マイグレーションを再実行**
   ```bash
   railway run python migrate_db.py  # Railway
   # または Render Shellから
   python migrate_db.py
   ```

### 静的ファイルが表示されない

- `static/` ディレクトリがGitに含まれているか確認
- ファイルのパーミッションを確認

---

## 📚 推奨開発フロー（Cursor使用時）

### 1. 機能追加・修正の流れ

```
1. Cursorでコードを編集
   ↓
2. ローカルで動作確認（http://localhost:5001）
   ↓
3. 問題なければGitコミット
   ↓
4. GitHubにプッシュ
   ↓
5. 自動デプロイを待つ
   ↓
6. 本番環境で動作確認
```

### 2. ブランチ戦略（オプション）

より安全な開発のため、ブランチを使用することもできます：

```bash
# 機能ブランチを作成
git checkout -b feature/password-visibility

# 開発・コミット
git add .
git commit -m "パスワード表示機能を追加"

# メインブランチにマージ
git checkout main
git merge feature/password-visibility
git push origin main
```

### 3. 環境変数の管理

**ローカル開発用 `.env` ファイル（Gitに含めない）:**

```bash
DATABASE_URL=sqlite:///connectplus.db
SESSION_SECRET=dev-secret-key
FLASK_DEBUG=True
```

**本番環境:**
- Railway/Renderの環境変数で設定
- `.env` ファイルは使用しない

---

## 🎯 まとめ

### 推奨デプロイ先

- **初心者・小規模運用**: **Railway** または **Render**
- **本格運用**: **VPS** (DigitalOcean、Linodeなど)

### 継続開発のベストプラクティス

1. ✅ **ローカルでテストしてからデプロイ**
2. ✅ **意味のあるコミットメッセージを書く**
3. ✅ **データベースマイグレーションは慎重に**
4. ✅ **本番環境のログを定期的に確認**
5. ✅ **環境変数は本番環境で管理**

### 次のステップ

1. 現在の変更をコミット・プッシュ
2. RailwayまたはRenderでデプロイ
3. 本番環境で動作確認
4. 以降は、ローカル開発 → コミット → プッシュ → 自動デプロイのサイクル

---

**質問や問題があれば、お気軽にお尋ねください！**

