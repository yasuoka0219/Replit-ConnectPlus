# SMTP設定手順

## ✅ ステップ1とステップ2の実行結果

### ステップ1: SMTP設定のテスト ✅

`test_smtp.py`を実行しました。現在、SMTP設定が未設定のため、設定が必要です。

### ステップ2: 環境変数の設定 ✅

`.env`ファイルにSMTP設定のテンプレートを追加しました。

---

## 📝 次のステップ：実際のSMTP設定を入力

`.env`ファイルに以下の値を実際の値に置き換えてください：

### 1. Gmailアプリパスワードの取得

1. **Googleアカウント設定にアクセス**
   - https://myaccount.google.com/security

2. **2段階認証を有効化**（まだの場合）
   - 「2段階認証プロセス」を有効化

3. **アプリパスワードを生成**
   - 「アプリパスワード」を選択
   - 「アプリを選択」→「メール」を選択
   - 「デバイスを選択」→「その他（カスタム名）」を選択
   - 名前を入力：`CONNECT+ CRM`
   - 「生成」をクリック
   - **16文字のパスワードをコピー**（一度しか表示されません）

### 2. .envファイルを編集

`.env`ファイルを開いて、以下の値を実際の値に置き換えてください：

```bash
# SMTP設定（メール送信用）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com          # ← 実際のGmailアドレスに置き換え
SMTP_PASSWORD=your-16-digit-app-password    # ← 生成した16文字のアプリパスワードに置き換え
SMTP_FROM_EMAIL=your-email@gmail.com        # ← 実際のGmailアドレスに置き換え
SMTP_FROM_NAME=CONNECT+ CRM
```

**例：**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=example@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=example@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

### 3. 設定の確認

`.env`ファイルを編集した後、再度テストを実行：

```bash
python3 test_smtp.py
```

テストメールの送信先メールアドレスを入力すると、メールが送信されます。

---

## 🔍 現在の.envファイルの状態

現在、`.env`ファイルには以下のテンプレートが設定されています：

```bash
DATABASE_URL=sqlite:///connectplus.db
SESSION_SECRET=dev-secret-key-change-this-in-production

# SMTP設定（メール送信用）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**重要**: `SMTP_USERNAME`、`SMTP_PASSWORD`、`SMTP_FROM_EMAIL`を実際の値に置き換えてください。

---

## 📚 参考資料

- [Gmail SMTP設定ガイド](./GMAIL_SMTP_SETUP.md)
- [実装手順](./IMPLEMENTATION_STEPS.md)

---

## 🎯 まとめ

1. ✅ `.env`ファイルにSMTP設定のテンプレートを追加
2. ⏳ **次**: 実際のGmailアプリパスワードを取得して`.env`ファイルに設定
3. ⏳ **その後**: `python3 test_smtp.py`を実行してテスト

Gmailアプリパスワードを取得したら、`.env`ファイルを編集して実際の値を設定してください。
