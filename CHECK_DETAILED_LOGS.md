# 詳細なエラーログの確認方法

## 🔴 確認されたエラー

HTTP Logsで以下のエラーが確認されました：

```
POST /api/2fa/setup → HTTP Status 500 (Internal Server Error)
処理時間: 30秒
```

これは、2段階認証設定時にサーバー側でエラーが発生していることを示しています。

---

## 🔍 詳細なエラーログを確認する方法

### ステップ1: Deploy Logsを確認

HTTP Logsでは詳細なエラーメッセージが見えないため、Deploy Logsまたはアプリケーションのログを確認する必要があります。

1. **Railwayダッシュボードを開く**
   - https://railway.app にアクセス
   - プロジェクトを選択
   - 「web」サービスを選択

2. **「Deploy Logs」タブを開く**
   - 上部のタブから「Deploy Logs」を選択
   - または、「HTTP Logs」の横にある「Deploy Logs」をクリック

3. **エラーログを確認**
   - `[2FA Setup]` で始まるログを探す
   - `[2FA Email]` で始まるログを探す
   - エラーメッセージの全文を確認

### ステップ2: アプリケーションのログを確認

1. **「HTTP Logs」タブで検索**
   - 検索バーに `[2FA` と入力
   - または、`error` と入力してエラーログを探す

2. **ログの詳細を確認**
   - 各ログエントリをクリックして詳細を確認
   - エラーメッセージの全文を確認

---

## 🔧 考えられる原因

### 原因1: メール送信のタイムアウト

**症状:**
- 処理に30秒かかっている
- メール送信がタイムアウトしている可能性

**確認方法:**
- ログに `[2FA Email] 試行 1/3: ポート 587 で接続中...` が表示されているか確認
- タイムアウトエラーが表示されているか確認

**解決方法:**
- SendGridのAPIキーが正しく設定されているか確認
- ポート465を試す（環境変数で `SMTP_PORT=465` に変更）

### 原因2: データベースエラー

**症状:**
- `Email2FACode` テーブルが存在しない
- データベース接続エラー

**確認方法:**
- ログに `no such table: email2facode` や `relation "email2facode" does not exist` などのエラーがないか確認

**解決方法:**
- マイグレーションを実行（通常は自動で実行されますが、必要に応じて手動で実行）

### 原因3: SendGridのAPIキーが無効

**症状:**
- SMTP認証エラー
- メール送信に失敗

**確認方法:**
- ログに `SMTP認証エラー` や `SMTPAuthenticationError` が表示されているか確認

**解決方法:**
- SendGridダッシュボードでAPIキーを確認
- Railwayで `SMTP_PASSWORD` を再確認

---

## 🛠️ 即座に試せる対処法

### 方法1: ログから認証コードを確認

メール送信に失敗しても、ログに認証コードが表示される場合があります：

1. Railwayダッシュボード → 「Deploy Logs」または「HTTP Logs」
2. `[2FA Setup] 認証コード（ログから確認）:` で始まるログを探す
3. 認証コードをコピー
4. 2段階認証設定画面で認証コードを入力

### 方法2: 環境変数を再確認

1. Railwayダッシュボード → 「Variables」
2. すべてのSMTP関連の環境変数を確認：

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxx...（SendGridのAPIキー）
SMTP_FROM_EMAIL=noreply@bizcraft-studio.com
SMTP_FROM_NAME=CONNECT+ CRM
```

3. 誤りがあれば修正
4. 再デプロイ

### 方法3: ポートを変更してみる

1. Railwayダッシュボード → 「Variables」
2. `SMTP_PORT` を `587` から `465` に変更
3. 保存
4. 再デプロイ

---

## 📋 確認すべきログ

以下のようなログを探してください：

### 正常な場合
```
[2FA Setup] User xxx@example.com (ID: 1) initiated 2FA setup. Code ID: 1
[2FA Email] 試行 1/3: ポート 587 で接続中...
[2FA Email] ✓ Code sent to xxx@example.com (ポート 587)
```

### エラーの場合
```
[2FA Setup] メール送信で例外が発生: ...
[2FA Email] ❌ SMTP認証エラー: ...
[2FA Email] ❌ SMTPエラー: ...
[2FA Setup] 認証コード（ログから確認）: 123456
```

---

## 💡 次のステップ

1. **「Deploy Logs」タブを開く**
2. **`[2FA` で検索**
3. **エラーメッセージの全文を確認**
4. **エラーメッセージを共有**

エラーメッセージの全文が分かれば、より具体的な解決方法を提案できます。

---

**まず、「Deploy Logs」タブで `[2FA` と検索して、エラーメッセージの全文を確認してください！**
