# ローカル環境セットアップガイド

このガイドでは、CONNECT+ CRMアプリケーションをローカル環境で実行する手順を説明します。

## 前提条件

- Python 3.11以上
- `uv` パッケージマネージャー（または `pip`）

## セットアップ手順

### 1. 依存関係のインストール

#### uvを使用する場合（推奨）

```bash
# uvがインストールされていない場合
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係のインストール
uv sync
```

#### pipを使用する場合

```bash
# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルが既に作成されている場合は、必要に応じて編集してください。

```bash
# .envファイルを編集
# DATABASE_URLとSESSION_SECRETを設定
```

**SQLiteを使用する場合（開発用・推奨）:**
```
DATABASE_URL=sqlite:///connectplus.db
SESSION_SECRET=dev-secret-key-change-this-in-production
```

**PostgreSQLを使用する場合:**
```
DATABASE_URL=postgresql://username:password@localhost:5432/connectplus
SESSION_SECRET=your-secret-key-here
```

### 3. データベースの初期化

```bash
python migrate_db.py
```

このコマンドでデータベーススキーマが作成されます。

### 4. デモデータの投入（オプション）

テスト用のサンプルデータを投入する場合:

```bash
python seed.py
```

デモアカウント情報:
- **メールアドレス**: demo@example.com
- **パスワード**: demo1234

### 5. アプリケーションの起動

```bash
python app.py
```

アプリケーションは `http://localhost:5000` で起動します。

ブラウザでアクセスして、ログイン画面が表示されることを確認してください。

## トラブルシューティング

### データベース接続エラー

- `.env`ファイルの`DATABASE_URL`が正しく設定されているか確認してください
- SQLiteを使用する場合、`connectplus.db`ファイルへの書き込み権限があるか確認してください
- PostgreSQLを使用する場合、データベースサーバーが起動しているか確認してください

### 依存関係のインストールエラー

- Pythonのバージョンが3.11以上であることを確認してください
- `uv`または`pip`が最新版であることを確認してください

### マイグレーションエラー

- 既存のデータベースファイルがある場合、削除してから再度`migrate_db.py`を実行してください
- SQLiteを使用している場合、ファイルの権限を確認してください

## 次のステップ

- 新規ユーザーを登録する: `/register`
- デモデータでログインする: `demo@example.com` / `demo1234`
- 企業・案件・タスクを管理する

## 開発時の注意事項

- 本番環境では必ず`SESSION_SECRET`を変更してください
- 本番環境ではPostgreSQLの使用を推奨します
- 定期的にデータベースのバックアップを取得してください















