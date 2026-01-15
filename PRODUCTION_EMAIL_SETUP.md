# 本番環境でのメール機能実装手順

CONNECT+ CRMの2段階認証メール送信機能を本番環境で有効化するための完全ガイドです。

## 📋 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [メール送信サービスの選択](#メール送信サービスの選択)
4. [Railwayでの実装手順](#railwayでの実装手順)
5. [Renderでの実装手順](#renderでの実装手順)
6. [Herokuでの実装手順](#herokuでの実装手順)
7. [VPSでの実装手順](#vpsでの実装手順)
8. [動作確認](#動作確認)
9. [トラブルシューティング](#トラブルシューティング)
10. [セキュリティチェックリスト](#セキュリティチェックリスト)

---

## 概要

CONNECT+ CRMでは以下のメール機能が利用可能です：

- **2段階認証コード送信**: ログイン時にメールで認証コードを送信
- **2FA設定時の認証コード送信**: 2段階認証を有効化する際の確認コード
- **パスワードリセットメール**: パスワード忘れ時のリセットリンク送信

これらの機能を本番環境で動作させるには、SMTP設定が必要です。

## ✅ 独自ドメインは不要です！

**既存のメールアドレス（Gmail、Outlookなど）でそのまま使用できます。**  
SendGridの「Single Sender Verification」を使用すれば、独自ドメインなしでメール送信が可能です。

詳細は [独自ドメインの必要性](./DOMAIN_REQUIREMENT.md) を参照してください。

---

## 前提条件

- 本番環境のデプロイが完了していること
- データベースが正常に動作していること
- 管理者アカウントでログインできること

---

## メール送信サービスの選択

### 推奨サービス（優先順）

1. **SendGrid** ⭐⭐⭐⭐⭐
   - 無料プラン: 1日100通まで
   - 設定が簡単
   - 信頼性が高い
   - **独自ドメイン不要**（既存メールアドレスでOK）

2. **Mailgun** ⭐⭐⭐⭐
   - 無料プラン: 最初の3ヶ月で5,000通/月
   - 高機能
   - APIが充実

3. **Amazon SES** ⭐⭐⭐⭐
   - 低コスト（$0.10/1,000通）
   - AWS環境との統合が容易
   - 初期設定がやや複雑

4. **Gmail SMTP** ⭐⭐⭐
   - 無料
   - アプリパスワードが必要
   - 送信制限あり（1日500通）
   - 本番環境では非推奨

### サービス別の特徴

| サービス | 無料枠 | 設定難易度 | 信頼性 | 推奨度 |
|---------|--------|----------|--------|--------|
| SendGrid | 100通/日 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Mailgun | 5,000通/月（3ヶ月） | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Amazon SES | 62,000通/月（AWS利用時） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Gmail | 500通/日 | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## Railwayでの実装手順

### ステップ1: SendGridアカウントの作成

1. https://sendgrid.com にアクセス
2. 「Sign Up」をクリックしてアカウントを作成
3. メールアドレスを確認（確認メールが届きます）

### ステップ2: SendGrid APIキーの生成

1. SendGridダッシュボードにログイン
2. 左メニューから「Settings」→「API Keys」を選択
3. 「Create API Key」をクリック
4. 設定：
   - **API Key Name**: `CONNECT+ CRM Production`
   - **API Key Permissions**: 「Full Access」を選択（または「Restricted Access」→「Mail Send」のみ）
5. 「Create & View」をクリック
6. **APIキーをコピー**（一度しか表示されません！）
   - 例: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### ステップ3: 送信元メールアドレスの確認

1. SendGridダッシュボード → 「Settings」→ 「Sender Authentication」
2. 「Single Sender Verification」を選択
3. 「Create a Sender」をクリック
4. 以下の情報を入力：
   - **From Email Address**: 送信元メールアドレス（例: `your-email@gmail.com`）
     - ✅ 既存のメールアドレス（Gmail、Outlookなど）でOK
     - ❌ 独自ドメインは不要
   - **From Name**: `CONNECT+ CRM`
   - **Reply To**: 同じメールアドレス
   - **Company Address**: 会社の住所（任意）
5. 「Create」をクリック
6. 確認メールが送信されるので、メールを確認してリンクをクリック
7. 確認が完了すると「Verified」と表示されます

### ステップ4: Railwayで環境変数を設定

1. Railwayダッシュボードにログイン
2. プロジェクトを選択
3. 「Variables」タブを開く
4. 以下の環境変数を追加：

```bash
# SMTP設定（SendGrid）
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=your-email@gmail.com  # 既存のメールアドレスでOK（独自ドメイン不要）
SMTP_FROM_NAME=CONNECT+ CRM
```

**重要**: 
- `SMTP_USERNAME`は必ず`apikey`に設定してください
- `SMTP_PASSWORD`にはSendGridのAPIキーを貼り付けます
- `SMTP_FROM_EMAIL`はSendGridで確認済みのメールアドレスを使用してください

### ステップ5: デプロイの再起動

1. Railwayダッシュボード → 「Deployments」
2. 最新のデプロイメントの「⋯」→「Redeploy」
3. または、GitHubにプッシュして自動デプロイをトリガー

### ステップ6: 動作確認

1. アプリケーションにログイン
2. 「設定」→「2段階認証設定」を開く
3. 「2段階認証を設定する（メール認証）」をクリック
4. メールで認証コードを受信（数秒～1分）
5. 認証コードを入力して有効化

---

## Renderでの実装手順

### ステップ1-3: SendGridの設定

Railwayと同様に、SendGridアカウントを作成し、APIキーと送信元メールアドレスを設定します。

### ステップ4: Renderで環境変数を設定

1. Renderダッシュボードにログイン
2. サービスを選択
3. 「Environment」タブを開く
4. 「Add Environment Variable」をクリック
5. 以下の環境変数を追加：

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=your-email@gmail.com  # 既存のメールアドレスでOK（独自ドメイン不要）
SMTP_FROM_NAME=CONNECT+ CRM
```

### ステップ5: デプロイの再起動

1. Renderダッシュボード → 「Manual Deploy」→「Deploy latest commit」
2. または、GitHubにプッシュして自動デプロイをトリガー

### ステップ6: 動作確認

Railwayと同様に動作確認を行います。

---

## Herokuでの実装手順

### ステップ1-3: SendGridの設定

Railwayと同様に、SendGridアカウントを作成し、APIキーと送信元メールアドレスを設定します。

### ステップ4: Herokuで環境変数を設定

```bash
# Heroku CLIでログイン
heroku login

# アプリを選択
cd /path/to/your/app

# 環境変数を設定
heroku config:set SMTP_SERVER=smtp.sendgrid.net
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USERNAME=apikey
heroku config:set SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
heroku config:set SMTP_FROM_EMAIL=your-email@gmail.com  # 既存のメールアドレスでOK（独自ドメイン不要）
heroku config:set SMTP_FROM_NAME="CONNECT+ CRM"
```

### ステップ5: デプロイの再起動

```bash
# アプリを再起動
heroku restart
```

### ステップ6: 動作確認

Railwayと同様に動作確認を行います。

---

## VPSでの実装手順

### ステップ1-3: SendGridの設定

Railwayと同様に、SendGridアカウントを作成し、APIキーと送信元メールアドレスを設定します。

### ステップ4: .envファイルに環境変数を追加

```bash
# サーバーにSSH接続
ssh user@your-server-ip

# アプリケーションディレクトリに移動
cd /var/www/connectplus

# .envファイルを編集
nano .env
```

`.env`ファイルに以下を追加：

```bash
# SMTP設定（SendGrid）
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=your-email@gmail.com  # 既存のメールアドレスでOK（独自ドメイン不要）
SMTP_FROM_NAME=CONNECT+ CRM
```

### ステップ5: アプリケーションの再起動

```bash
# systemdサービスを再起動
sudo systemctl restart connectplus

# ログを確認
sudo journalctl -u connectplus -f
```

### ステップ6: 動作確認

Railwayと同様に動作確認を行います。

---

## 動作確認

### 1. 2段階認証の設定

1. アプリケーションにログイン
2. 「設定」→「2段階認証設定」を開く
3. 「2段階認証を設定する（メール認証）」をクリック
4. メールで認証コードを受信（数秒～1分）
5. 認証コードを入力して有効化
6. 「2段階認証が有効です」と表示されれば成功

### 2. ログイン時の2段階認証

1. ログアウト
2. メールアドレスとパスワードでログイン
3. メールで認証コードを受信
4. 認証コードを入力してログイン完了

### 3. パスワードリセット

1. ログイン画面で「パスワードを忘れた場合」をクリック
2. メールアドレスを入力
3. メールでリセットリンクを受信
4. リンクをクリックしてパスワードをリセット

### 4. ログの確認

本番環境のログで以下を確認：

```bash
# Railwayの場合
railway logs

# Renderの場合
# ダッシュボードの「Logs」タブを確認

# Herokuの場合
heroku logs --tail

# VPSの場合
sudo journalctl -u connectplus -f
```

正常に動作している場合、以下のようなログが表示されます：

```
[2FA Email] ✓ Code sent to user@example.com
```

---

## トラブルシューティング

### 問題1: メールが届かない

**原因と対処法：**

1. **SMTP設定の確認**
   - 環境変数が正しく設定されているか確認
   - `SMTP_USERNAME`が`apikey`になっているか確認（SendGridの場合）
   - `SMTP_PASSWORD`にAPIキーが正しく設定されているか確認

2. **送信元メールアドレスの確認**
   - SendGridで送信元メールアドレスが「Verified」になっているか確認
   - 確認メールが届いていない場合は、スパムフォルダを確認

3. **ログの確認**
   - 本番環境のログでエラーメッセージを確認
   - `[2FA Email] ❌`で始まるエラーメッセージがないか確認

4. **スパムフォルダの確認**
   - 受信者のスパムフォルダを確認
   - 必要に応じて、送信元メールアドレスをホワイトリストに追加

### 問題2: SMTP認証エラー

**エラーメッセージ：**
```
[2FA Email] ❌ SMTP認証エラー: ...
```

**対処法：**

1. **APIキーの確認**
   - SendGridのAPIキーが正しいか確認
   - APIキーに権限（Mail Send）があるか確認

2. **ユーザー名の確認**
   - SendGridの場合、`SMTP_USERNAME`は必ず`apikey`に設定

3. **パスワードの確認**
   - APIキーに余分なスペースや改行が含まれていないか確認
   - コピー&ペースト時に文字化けしていないか確認

### 問題3: メール送信が遅い

**対処法：**

1. **SendGridのステータスを確認**
   - https://status.sendgrid.com でSendGridのステータスを確認

2. **送信制限の確認**
   - SendGridの無料プランは1日100通まで
   - 制限に達している場合は、有料プランにアップグレード

3. **ログの確認**
   - タイムアウトエラーがないか確認
   - ネットワーク接続の問題がないか確認

### 問題4: 開発モードで動作している

**ログに表示される：**
```
[2FA Email] ⚠️ SMTP設定がありません。開発モードで動作しています。
```

**対処法：**

1. **環境変数の確認**
   - 本番環境で環境変数が正しく設定されているか確認
   - 環境変数名が正しいか確認（大文字小文字を確認）

2. **デプロイの再起動**
   - 環境変数を変更した後、アプリケーションを再起動

3. **.envファイルの確認（VPSの場合）**
   - `.env`ファイルが正しく読み込まれているか確認
   - systemdサービスで環境変数が読み込まれているか確認

---

## セキュリティチェックリスト

本番環境でメール機能を有効化する前に、以下を確認してください：

- [ ] **SMTP認証情報の保護**
  - 環境変数に設定（コードに直接書かない）
  - ログに認証情報が出力されないことを確認

- [ ] **送信元メールアドレスの確認**
  - SendGridで送信元メールアドレスを確認済み
  - ドメイン認証を設定（可能な場合）

- [ ] **送信制限の設定**
  - SendGridで送信制限を設定（必要に応じて）
  - レート制限を設定（必要に応じて）

- [ ] **ログの監視**
  - メール送信エラーを監視
  - 異常な送信量を監視

- [ ] **バックアッププランの準備**
  - メール送信サービスがダウンした場合の対応
  - ログから認証コードを確認できることを確認

---

## その他のメール送信サービス

### Mailgunを使用する場合

```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-api-key
SMTP_FROM_EMAIL=your-email@gmail.com  # 既存のメールアドレスでOK（独自ドメイン不要）
SMTP_FROM_NAME=CONNECT+ CRM
```

### Amazon SESを使用する場合

```bash
SMTP_SERVER=email-smtp.region.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=your-email@gmail.com  # 既存のメールアドレスでOK（独自ドメイン不要）
SMTP_FROM_NAME=CONNECT+ CRM
```

**注意**: Amazon SESを使用する場合、送信元メールアドレスまたはドメインを確認する必要があります。

### Gmail SMTPを使用する場合（非推奨）

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**注意**: 
- Gmailのアプリパスワードが必要です
- 送信制限（1日500通）があります
- 本番環境では非推奨です

---

## 参考リンク

- [SendGrid公式ドキュメント](https://docs.sendgrid.com/)
- [Mailgun公式ドキュメント](https://documentation.mailgun.com/)
- [Amazon SES公式ドキュメント](https://docs.aws.amazon.com/ses/)
- [CONNECT+ CRM メール認証セットアップガイド](./EMAIL_2FA_SETUP.md)
- [CONNECT+ CRM SMTP設定ガイド](./SMTP_SETUP_GUIDE.md)

---

## サポート

問題が解決しない場合は、以下を確認してください：

1. 本番環境のログを確認
2. SendGrid（または使用しているサービス）のステータスページを確認
3. 環境変数が正しく設定されているか再確認
4. アプリケーションを再起動

**重要**: メールが届かない場合でも、本番環境のログに認証コードが表示されます。ログから認証コードを確認して、一時的に2段階認証を設定・ログインすることができます。

---

**最終更新**: 2025年1月
