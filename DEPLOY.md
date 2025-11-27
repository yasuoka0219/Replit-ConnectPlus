# 本番環境デプロイガイド

CONNECT+ CRMアプリケーションを本番環境にデプロイする手順を説明します。

## 📋 デプロイ前の準備

### 1. セキュリティ設定の確認

本番環境では必ず以下を変更してください：

- **SESSION_SECRET**: 強力なランダム文字列に変更
- **DATABASE_URL**: 本番用のPostgreSQLデータベースを使用
- **デバッグモード**: `debug=False`に設定

### 2. 環境変数の準備

本番環境で必要な環境変数：

```bash
DATABASE_URL=postgresql://username:password@host:5432/database_name
SESSION_SECRET=your-very-secure-random-string-here
PORT=5000  # プラットフォームによって自動設定される場合あり
```

**SESSION_SECRETの生成方法：**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 デプロイ方法

### 方法1: Heroku（推奨・簡単）

#### 前提条件
- Herokuアカウント（無料プランあり）
- Heroku CLIのインストール

#### 手順

1. **Heroku CLIのインストール**
```bash
# macOS
brew tap heroku/brew && brew install heroku

# ログイン
heroku login
```

2. **Herokuアプリの作成**
```bash
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
heroku create your-app-name
```

3. **PostgreSQLアドオンの追加**
```bash
heroku addons:create heroku-postgresql:mini
```

4. **環境変数の設定**
```bash
heroku config:set SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
```

5. **Procfileの作成**
```bash
echo "web: gunicorn app:app" > Procfile
```

6. **gunicornの追加**
`requirements.txt`に以下を追加：
```
gunicorn>=21.2.0
```

7. **デプロイ**
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

8. **データベースの初期化**
```bash
heroku run python migrate_db.py
```

9. **アプリケーションの確認**
```bash
heroku open
```

#### 注意点
- Herokuの無料プランは2022年11月で終了しましたが、有料プラン（Eco Dyno: $5/月）で利用可能
- 30分間アクセスがないとスリープするため、本格運用にはStandard Dyno（$25/月）を推奨

---

### 方法2: Railway（推奨・モダン）

#### 前提条件
- Railwayアカウント（GitHubアカウントでサインアップ可能）
- GitHubリポジトリ

#### 手順

1. **GitHubにリポジトリを作成**
```bash
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/connectplus.git
git push -u origin main
```

2. **Railwayでプロジェクトを作成**
   - https://railway.app にアクセス
   - "New Project" → "Deploy from GitHub repo" を選択
   - リポジトリを選択

3. **PostgreSQLデータベースの追加**
   - Railwayダッシュボードで "New" → "Database" → "Add PostgreSQL"
   - 自動的に`DATABASE_URL`環境変数が設定されます

4. **環境変数の設定**
   - Railwayダッシュボードで "Variables" タブを開く
   - `SESSION_SECRET`を追加（ランダム文字列を生成）

5. **ビルド設定**
   - Railwayは自動的にPythonアプリを検出します
   - 必要に応じて`railway.json`を作成：
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

6. **デプロイ**
   - GitHubにプッシュすると自動デプロイされます
   - Railwayダッシュボードでログを確認

7. **データベースの初期化**
   - Railway CLIを使用：
```bash
railway run python migrate_db.py
```

#### 料金
- 無料プランあり（$5クレジット/月）
- 使用量に応じた従量課金

---

### 方法3: Render（無料プランあり）

#### 前提条件
- Renderアカウント（GitHubアカウントでサインアップ可能）

#### 手順

1. **GitHubにリポジトリを作成**（Railwayと同様）

2. **RenderでWebサービスを作成**
   - https://render.com にアクセス
   - "New" → "Web Service" を選択
   - GitHubリポジトリを接続

3. **設定**
   - **Name**: アプリ名
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **PostgreSQLデータベースの追加**
   - "New" → "PostgreSQL" を選択
   - 自動的に`DATABASE_URL`環境変数が設定されます

5. **環境変数の設定**
   - "Environment" タブで `SESSION_SECRET` を追加

6. **デプロイ**
   - "Create Web Service" をクリック
   - 自動的にビルドとデプロイが開始されます

7. **データベースの初期化**
   - Render Shellを使用：
```bash
# Renderダッシュボードで "Shell" を開く
python migrate_db.py
```

#### 料金
- 無料プランあり（スリープあり）
- 有料プラン（$7/月）でスリープなし

---

### 方法4: VPS（DigitalOcean、Linodeなど）

#### 前提条件
- VPSサーバー（Ubuntu 20.04/22.04推奨）
- SSHアクセス

#### 手順

1. **サーバーのセットアップ**
```bash
# サーバーにSSH接続
ssh user@your-server-ip

# システムの更新
sudo apt update && sudo apt upgrade -y

# Pythonと必要なパッケージのインストール
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx git -y
```

2. **PostgreSQLの設定**
```bash
# PostgreSQLに接続
sudo -u postgres psql

# データベースとユーザーを作成
CREATE DATABASE connectplus;
CREATE USER connectplus_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE connectplus TO connectplus_user;
\q
```

3. **アプリケーションのデプロイ**
```bash
# アプリケーションディレクトリの作成
mkdir -p /var/www/connectplus
cd /var/www/connectplus

# Gitリポジトリからクローン（またはファイルをアップロード）
git clone https://github.com/yourusername/connectplus.git .

# 仮想環境の作成と依存関係のインストール
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

4. **環境変数の設定**
```bash
# .envファイルの作成
nano .env
```

`.env`の内容：
```
DATABASE_URL=postgresql://connectplus_user:your-secure-password@localhost:5432/connectplus
SESSION_SECRET=your-very-secure-random-string
```

5. **データベースの初期化**
```bash
export $(cat .env | xargs)
python migrate_db.py
```

6. **Gunicornの設定**
```bash
# systemdサービスファイルの作成
sudo nano /etc/systemd/system/connectplus.service
```

`/etc/systemd/system/connectplus.service`の内容：
```ini
[Unit]
Description=CONNECT+ CRM Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/connectplus
Environment="PATH=/var/www/connectplus/venv/bin"
EnvironmentFile=/var/www/connectplus/.env
ExecStart=/var/www/connectplus/venv/bin/gunicorn --workers 3 --bind unix:/var/www/connectplus/connectplus.sock app:app

[Install]
WantedBy=multi-user.target
```

7. **サービスの起動**
```bash
sudo systemctl start connectplus
sudo systemctl enable connectplus
```

8. **Nginxの設定**
```bash
sudo nano /etc/nginx/sites-available/connectplus
```

`/etc/nginx/sites-available/connectplus`の内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/connectplus/connectplus.sock;
    }

    location /static {
        alias /var/www/connectplus/static;
    }
}
```

```bash
# シンボリックリンクの作成
sudo ln -s /etc/nginx/sites-available/connectplus /etc/nginx/sites-enabled/

# Nginxの設定確認と再起動
sudo nginx -t
sudo systemctl restart nginx
```

9. **SSL証明書の設定（Let's Encrypt）**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🔒 セキュリティチェックリスト

本番環境デプロイ前に確認：

- [ ] `SESSION_SECRET`を強力なランダム文字列に変更
- [ ] `debug=False`に設定（app.pyの最後の行）
- [ ] データベースパスワードを強力なものに変更
- [ ] HTTPSを有効化（SSL証明書の設定）
- [ ] ファイアウォールの設定（必要なポートのみ開放）
- [ ] 定期的なバックアップの設定
- [ ] ログの監視設定

---

## 📊 パフォーマンス最適化

### Gunicornのワーカー数設定

CPUコア数に応じて調整：
```bash
# CPUコア数を確認
nproc

# ワーカー数 = (2 × CPUコア数) + 1
# 例: 2コアの場合 → 5ワーカー
gunicorn --workers 5 --bind 0.0.0.0:5000 app:app
```

### データベース接続プール

`app.py`の`SQLALCHEMY_ENGINE_OPTIONS`で調整済みですが、必要に応じて最適化：

```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,  # 接続プールサイズ
    'max_overflow': 20,  # 最大オーバーフロー
    'pool_pre_ping': True,  # 接続の生存確認
}
```

---

## 🔄 デプロイ後のメンテナンス

### データベースのバックアップ

```bash
# PostgreSQLの場合
pg_dump -U connectplus_user connectplus > backup_$(date +%Y%m%d).sql

# リストア
psql -U connectplus_user connectplus < backup_20250101.sql
```

### ログの確認

```bash
# Gunicornのログ
sudo journalctl -u connectplus -f

# Nginxのログ
sudo tail -f /var/log/nginx/error.log
```

### アプリケーションの更新

```bash
cd /var/www/connectplus
git pull
source venv/bin/activate
pip install -r requirements.txt
python migrate_db.py  # 必要に応じて
sudo systemctl restart connectplus
```

---

## 🆘 トラブルシューティング

### アプリケーションが起動しない

1. ログを確認：
```bash
sudo journalctl -u connectplus -n 50
```

2. 環境変数を確認：
```bash
cd /var/www/connectplus
source venv/bin/activate
export $(cat .env | xargs)
python app.py
```

### データベース接続エラー

1. PostgreSQLが起動しているか確認：
```bash
sudo systemctl status postgresql
```

2. 接続情報を確認：
```bash
psql -U connectplus_user -d connectplus -h localhost
```

### 静的ファイルが表示されない

1. Nginxの設定を確認
2. ファイルのパーミッションを確認：
```bash
sudo chown -R www-data:www-data /var/www/connectplus/static
```

---

## 📝 推奨デプロイ先の比較

| プラットフォーム | 難易度 | 無料プラン | スリープ | 推奨度 |
|----------------|--------|----------|---------|--------|
| **Railway** | ⭐⭐ | あり | なし | ⭐⭐⭐⭐⭐ |
| **Render** | ⭐⭐ | あり | あり | ⭐⭐⭐⭐ |
| **Heroku** | ⭐⭐ | なし | なし | ⭐⭐⭐ |
| **VPS** | ⭐⭐⭐⭐ | なし | なし | ⭐⭐⭐⭐ |

**初心者向け**: Railway または Render  
**本格運用**: VPS（DigitalOcean、Linodeなど）

---

## 📚 参考リンク

- [Heroku公式ドキュメント](https://devcenter.heroku.com/)
- [Railway公式ドキュメント](https://docs.railway.app/)
- [Render公式ドキュメント](https://render.com/docs)
- [Gunicorn公式ドキュメント](https://docs.gunicorn.org/)
- [Nginx公式ドキュメント](https://nginx.org/en/docs/)

---

**デプロイに関する質問や問題があれば、お気軽にお尋ねください！**








