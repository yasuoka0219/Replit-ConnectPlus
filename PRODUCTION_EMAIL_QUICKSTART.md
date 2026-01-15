# 本番環境メール機能 クイックスタートガイド

本番環境でメール機能を最短で有効化する手順です。

## ✅ 独自ドメインは不要です！

**既存のメールアドレス（Gmail、Outlookなど）でそのまま使用できます。**  
詳細は [独自ドメインの必要性](./DOMAIN_REQUIREMENT.md) を参照してください。

## 🚀 5分で完了！SendGridを使用した設定

### ステップ1: SendGridアカウント作成（2分）

1. https://sendgrid.com にアクセス
2. 「Sign Up」をクリック
3. メールアドレスを確認

### ステップ2: APIキーの生成（1分）

1. SendGridダッシュボード → 「Settings」→「API Keys」
2. 「Create API Key」をクリック
3. 名前: `CONNECT+ CRM`
4. 権限: 「Full Access」を選択
5. 「Create & View」をクリック
6. **APIキーをコピー**（例: `SG.xxxxxxxx...`）

### ステップ3: 送信元メールアドレスの確認（1分）

1. SendGridダッシュボード → 「Settings」→「Sender Authentication」
2. 「Single Sender Verification」→「Create a Sender」
3. **既存のメールアドレスを入力**（例: `your-email@gmail.com`）
   - ✅ Gmail、Outlook、Yahooメールなど、既に持っているメールアドレスでOK
   - ❌ 独自ドメインは不要
4. 確認メールをクリックして承認

### ステップ4: 環境変数の設定（1分）

#### Railwayの場合

1. Railwayダッシュボード → プロジェクト → 「Variables」
2. 以下を追加：

```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=your-email@gmail.com  # 既存のメールアドレスでOK（独自ドメイン不要）
SMTP_FROM_NAME=CONNECT+ CRM
```

3. 「Deployments」→「Redeploy」

#### Renderの場合

1. Renderダッシュボード → サービス → 「Environment」
2. 上記の環境変数を追加
3. 「Manual Deploy」→「Deploy latest commit」

#### Herokuの場合

```bash
heroku config:set SMTP_SERVER=smtp.sendgrid.net
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USERNAME=apikey
heroku config:set SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
heroku config:set SMTP_FROM_EMAIL=your-email@gmail.com  # 既存のメールアドレスでOK
heroku config:set SMTP_FROM_NAME="CONNECT+ CRM"
heroku restart
```

#### VPSの場合

```bash
cd /var/www/connectplus
nano .env
```

`.env`ファイルに上記の環境変数を追加し、保存：

```bash
sudo systemctl restart connectplus
```

### ステップ5: 動作確認（1分）

1. アプリにログイン
2. 「設定」→「2段階認証設定」
3. 「2段階認証を設定する（メール認証）」をクリック
4. メールで認証コードを受信
5. コードを入力して有効化

✅ **完了！** メール機能が有効になりました。

---

## ⚠️ 重要な注意事項

1. **`SMTP_USERNAME`は必ず`apikey`に設定**（SendGridの場合）
2. **`SMTP_PASSWORD`にはAPIキー全体を貼り付け**（`SG.`で始まる文字列）
3. **`SMTP_FROM_EMAIL`はSendGridで確認済みのメールアドレスを使用**
   - ✅ 既存のメールアドレス（Gmail、Outlookなど）でOK
   - ❌ 独自ドメインは不要
4. **環境変数を変更した後は、アプリケーションを再起動**

---

## 🔍 トラブルシューティング

### メールが届かない場合

1. **ログを確認**
   ```bash
   # Railway
   railway logs
   
   # Render
   # ダッシュボードの「Logs」タブ
   
   # Heroku
   heroku logs --tail
   
   # VPS
   sudo journalctl -u connectplus -f
   ```

2. **環境変数を再確認**
   - `SMTP_USERNAME=apikey`になっているか
   - `SMTP_PASSWORD`にAPIキーが正しく設定されているか
   - `SMTP_FROM_EMAIL`がSendGridで確認済みか

3. **スパムフォルダを確認**

### ログから認証コードを確認

メールが届かなくても、ログに認証コードが表示されます：

```
[2FA Email] 認証コード: 123456
```

このコードを使用して一時的に2段階認証を設定・ログインできます。

---

## 📚 詳細な手順

より詳細な手順や、他のメール送信サービス（Mailgun、Amazon SESなど）を使用する場合は、[本番環境メール機能実装手順](./PRODUCTION_EMAIL_SETUP.md)を参照してください。

---

**所要時間**: 約5分  
**難易度**: ⭐⭐（簡単）
