# メール認証（Email-based 2FA）セットアップガイド

## 概要

CONNECT+ CRMでは、2段階認証として以下の2つの方法を選択できます：

1. **認証アプリ（推奨）**: Google Authenticatorなどの認証アプリを使用（QRコード）
2. **メール認証**: メールアドレスに送信される6桁のコードを使用

## メール認証の設定

### 1. SMTP設定

`.env`ファイルに以下の環境変数を追加してください：

```env
# SMTP設定（メール送信用）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

### 2. Gmailを使用する場合

1. **Googleアカウントの2段階認証を有効化**
2. **アプリパスワードを生成**:
   - Googleアカウント設定 → セキュリティ → 2段階認証プロセス → アプリパスワード
   - アプリを選択（メール）→ デバイスを選択 → 「生成」をクリック
   - 生成された16桁のパスワードをコピー

3. **.envファイルに設定**:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-digit-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   SMTP_FROM_NAME=CONNECT+ CRM
   ```

### 3. その他のメールプロバイダー

#### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

#### SendGrid
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

#### AWS SES
```env
SMTP_SERVER=email-smtp.region.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
```

## 使用方法

### 2段階認証の有効化

1. ログイン後、設定ページ（`/settings`）にアクセス
2. 「セキュリティ設定」→「2段階認証」→「設定」
3. **メール認証**を選択
4. 「2段階認証を設定する」ボタンをクリック
5. 登録されているメールアドレスに認証コードが送信されます
6. メールに記載されている6桁のコードを入力
7. 「確認して有効にする」ボタンをクリック

### ログイン時の使用

1. 通常通りメールアドレスとパスワードを入力してログイン
2. パスワードが正しい場合、メールに認証コードが自動送信されます
3. メールに記載されている6桁のコードを入力
4. ログイン完了

### コードの再送信

ログイン画面または設定画面で「コードを再送信する」ボタンをクリックすると、新しい認証コードがメールで送信されます。

## セキュリティ機能

- **有効期限**: 認証コードは10分間有効です
- **試行回数制限**: 3回まで試行可能です
- **コードの無効化**: 一度使用したコードは無効になります
- **古いコードの削除**: 新しいコードが送信されると、古いコードは自動的に無効になります

## トラブルシューティング

### メールが届かない場合

1. **SMTP設定を確認**: `.env`ファイルの設定が正しいか確認
2. **スパムフォルダを確認**: メールがスパムフォルダに移動している可能性があります
3. **メールアドレスの確認**: 登録されているメールアドレスが正しいか確認
4. **開発モード**: SMTP設定がない場合、コンソールにコードが表示されます（開発用）

### SMTPエラーの場合

1. **ファイアウォール設定**: SMTPポート（通常587）がブロックされていないか確認
2. **認証情報**: ユーザー名とパスワードが正しいか確認
3. **アプリパスワード**: Gmailを使用する場合は、通常のパスワードではなくアプリパスワードが必要です

## 注意事項

- メール認証コードは10分間のみ有効です
- 一度使用したコードは再利用できません
- 3回連続で間違ったコードを入力すると、コードが無効になります
- メールが届かない場合は、コードを再送信してください



