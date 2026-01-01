# メール送信設定ガイド（SendGrid使用）

GmailのSMTPサーバーに接続できない問題を解決するため、SendGridなどのメール送信サービスを使用する方法を説明します。

## SendGridを使用する方法（推奨）

### 1. SendGridアカウントの作成

1. https://sendgrid.com にアクセス
2. 「Sign Up」をクリックしてアカウントを作成
3. 無料プランで1日100通まで送信可能

### 2. APIキーの生成

1. SendGridダッシュボードにログイン
2. 左メニューから「Settings」→「API Keys」を選択
3. 「Create API Key」をクリック
4. 以下の設定：
   - **API Key Name**: `CONNECT+ CRM`
   - **API Key Permissions**: 「Full Access」を選択（または「Restricted Access」→「Mail Send」のみ）
5. 「Create & View」をクリック
6. **APIキーをコピー**（一度しか表示されません！）

### 3. Railwayでの環境変数設定

Railwayダッシュボードの「Variables」タブで、以下の環境変数を**更新または追加**：

```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=（SendGridのAPIキーを貼り付け）
SMTP_FROM_EMAIL=your-email@yourdomain.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**重要**: `SMTP_USERNAME`は必ず`apikey`に設定してください。

### 4. メールアドレスの確認（SendGrid）

SendGridでは、送信元メールアドレス（`SMTP_FROM_EMAIL`）を確認する必要があります：

1. SendGridダッシュボード → 「Settings」→ 「Sender Authentication」
2. 「Single Sender Verification」を選択
3. 「Create a Sender」をクリック
4. 送信元メールアドレスと情報を入力
5. 確認メールが送信されるので、メールを確認して承認

**注意**: 確認メールが届かない場合は、送信元メールアドレスが正しいか確認してください。

### 5. デプロイの再起動

環境変数を変更した後：
1. Railwayダッシュボード → 「Deployments」
2. 最新のデプロイメントの「⋯」→「Redeploy」

### 6. 動作確認

1. アプリケーションでログイン
2. 「設定」→「2段階認証設定」を開く
3. 「2段階認証を設定する（メール認証）」をクリック
4. メールで認証コードを受信（数秒～1分）
5. 認証コードを入力して有効化

## その他のメール送信サービス

### Mailgun

1. https://mailgun.com でアカウント作成
2. APIキーを取得
3. Railwayで設定：
   ```
   SMTP_SERVER=smtp.mailgun.org
   SMTP_PORT=587
   SMTP_USERNAME=postmaster@your-domain.mailgun.org
   SMTP_PASSWORD=（MailgunのAPIキー）
   ```

### Amazon SES

1. AWSアカウントでSESを有効化
2. SMTP認証情報を取得
3. Railwayで設定：
   ```
   SMTP_SERVER=email-smtp.region.amazonaws.com
   SMTP_PORT=587
   SMTP_USERNAME=（SESのSMTPユーザー名）
   SMTP_PASSWORD=（SESのSMTPパスワード）
   ```

## トラブルシューティング

### メールが届かない場合

1. **Railwayのログを確認**
   - ログに `[2FA Email] ✓ Code sent to ...` と表示されているか確認
   - エラーメッセージがないか確認

2. **環境変数の確認**
   - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`が正しく設定されているか
   - `SMTP_USERNAME`が`apikey`になっているか（SendGridの場合）

3. **送信元メールアドレスの確認**
   - SendGridで送信元メールアドレスが確認済みか
   - 確認メールが届いているか

4. **ログから認証コードを確認**
   - メールが届かなくても、Railwayのログに認証コードが表示されます
   - ログで `[2FA Email] 認証コード（開発用）: XXXXXX` を探してください

## 現在の状況

現在、GmailのSMTPサーバーへの接続ができないため、メールが届きません。SendGridなどのメール送信サービスを設定することで、確実にメールを送信できるようになります。

メール送信ができない場合でも、Railwayのログに認証コードが表示されるため、ログから認証コードを確認して2段階認証を設定・ログインすることができます。

