# 独自ドメインでのメール送信設定ガイド

## ✅ 概要

SendGridの「Domain Authentication」を使用することで、既に取得している独自ドメインからメールを送信できます。

**例:**
- ドメイン: `example.com`
- 送信元メールアドレス: `noreply@example.com` または `info@example.com`

---

## 🚀 設定手順

### ステップ1: SendGridアカウント作成（法人アカウント）

1. **SendGrid日本版にアクセス**
   - https://sendgrid.kke.co.jp にアクセス
   - 法人情報でアカウントを作成

2. **アカウント確認**
   - 確認メールをクリックして承認

### ステップ2: Domain Authenticationの設定（約10分）

1. **SendGridダッシュボードにログイン**
   - https://app.sendgrid.com にアクセス

2. **Domain Authenticationを設定**
   - 左メニュー → 「Settings」→「Sender Authentication」
   - 「Authenticate Your Domain」をクリック
   - 「Single Sender Verification」ではなく、「Domain Authentication」を選択

3. **ドメインを入力**
   - ドメイン名を入力（例: `example.com`）
   - サブドメインは使用しない（例: `mail.example.com`ではなく`example.com`）
   - 「Next」をクリック

4. **DNSレコードを確認**
   - SendGridが生成したDNSレコードが表示されます
   - 以下のようなレコードが表示されます：
     ```
     Type: CNAME
     Host: em1234.example.com
     Value: u1234567.wl123.sendgrid.net
     
     Type: CNAME
     Host: s1._domainkey.example.com
     Value: s1.domainkey.u1234567.wl123.sendgrid.net
     
     Type: CNAME
     Host: s2._domainkey.example.com
     Value: s2.domainkey.u1234567.wl123.sendgrid.net
     ```
   - **重要**: これらのレコードをコピーしておく

### ステップ3: DNSレコードを追加（約5分）

1. **ドメイン管理画面にアクセス**
   - ドメインを取得したサービス（お名前.com、ムームードメイン、Route53など）にログイン

2. **DNS設定を開く**
   - ドメイン管理 → DNS設定
   - 「DNSレコードの設定」または「DNS設定」を開く

3. **CNAMEレコードを追加**
   - SendGridで表示されたCNAMEレコードを追加
   - 例：
     ```
     Type: CNAME
     Name: em1234
     Value: u1234567.wl123.sendgrid.net
     TTL: 3600（または自動）
     
     Type: CNAME
     Name: s1._domainkey
     Value: s1.domainkey.u1234567.wl123.sendgrid.net
     TTL: 3600
     
     Type: CNAME
     Name: s2._domainkey
     Value: s2.domainkey.u1234567.wl123.sendgrid.net
     TTL: 3600
     ```

4. **DNSの反映を待つ**
   - 通常、数分〜数時間かかります
   - 最大48時間かかる場合があります

### ステップ4: Domain Authenticationの確認（約5分）

1. **SendGridダッシュボードに戻る**
   - 「Settings」→「Sender Authentication」
   - 設定したドメインを選択

2. **「Verify」をクリック**
   - SendGridがDNSレコードを確認します
   - すべてのレコードが正しく設定されていれば「Verified」と表示されます

3. **確認が完了するまで待つ**
   - すべてのレコードが確認されるまで数分かかる場合があります
   - 「Verified」と表示されるまで待ちます

### ステップ5: APIキーの生成（1分）

1. **APIキーを作成**
   - 左メニュー → 「Settings」→「API Keys」
   - 「Create API Key」をクリック
   - 名前: `CONNECT+ CRM`
   - 権限: 「Full Access」を選択
   - 「Create & View」をクリック

2. **APIキーをコピー**
   - APIキーをコピー（例: `SG.xxxxxxxx...`）
   - 安全な場所に保存

### ステップ6: Railwayで環境変数を設定（1分）

1. **Railwayダッシュボードを開く**
   - https://railway.app にアクセス
   - プロジェクトを選択
   - 「web」サービスを選択

2. **環境変数を追加/更新**
   - 「Variables」タブを開く
   - 以下の環境変数を設定：

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**重要:**
- `SMTP_USERNAME`は必ず`apikey`（そのまま）
- `SMTP_PASSWORD`には生成したAPIキー全体を貼り付け
- `SMTP_FROM_EMAIL`は独自ドメインのメールアドレス（例: `noreply@example.com`）
  - このメールアドレスは実際に存在する必要はありません（SendGridが処理します）

3. **保存して再デプロイ**
   - 環境変数を保存
   - 「Deployments」タブ → 「Redeploy」をクリック

### ステップ7: 動作確認（1分）

1. **アプリケーションにアクセス**
   - RailwayのURLにアクセス
   - ログイン

2. **2段階認証を設定**
   - 「設定」→「2段階認証設定」
   - 「2段階認証を設定する（メール認証）」をクリック

3. **メールを確認**
   - 設定したメールアドレス（例: `noreply@example.com`）から認証コードが届くことを確認
   - 認証コードを入力して2段階認証を有効化

✅ **完了！** 独自ドメインからメールが正常に送信されるようになりました。

---

## 🔍 トラブルシューティング

### DNSレコードが反映されない場合

1. **DNSの反映を確認**
   ```bash
   # コマンドラインで確認
   nslookup em1234.example.com
   nslookup s1._domainkey.example.com
   nslookup s2._domainkey.example.com
   ```

2. **DNS設定を再確認**
   - ドメイン管理画面でCNAMEレコードが正しく設定されているか確認
   - タイポがないか確認

3. **時間を置いて再試行**
   - DNSの反映には時間がかかります
   - 数時間待ってから再度「Verify」をクリック

### Domain Authenticationが確認できない場合

1. **すべてのCNAMEレコードが設定されているか確認**
   - SendGridで表示されたすべてのレコードを追加する必要があります

2. **ドメイン名の入力ミスを確認**
   - サブドメインではなく、ルートドメインを使用しているか確認

3. **SendGridサポートに問い合わせ**
   - 問題が解決しない場合は、SendGridサポートに問い合わせ

### メールが届かない場合

1. **環境変数を確認**
   - `SMTP_FROM_EMAIL`が独自ドメインのメールアドレスになっているか確認
   - 例: `noreply@example.com`（`example.com`は実際のドメイン名）

2. **SendGridで確認**
   - SendGridダッシュボード → 「Activity」
   - メール送信の履歴を確認
   - エラーがある場合は詳細を確認

3. **スパムフォルダを確認**
   - メールがスパムフォルダに入っている可能性があります

---

## 📋 チェックリスト

- [ ] SendGrid法人アカウントを作成
- [ ] Domain Authenticationを設定
- [ ] DNSレコードを追加
- [ ] Domain Authenticationを確認（Verified）
- [ ] APIキーを生成
- [ ] Railwayで環境変数を設定
- [ ] 再デプロイ
- [ ] 2段階認証設定を試す
- [ ] メールが届くことを確認

---

## 💡 補足情報

### 送信元メールアドレスの選択

独自ドメインを使用する場合、以下のようなメールアドレスが一般的です：

- `noreply@example.com` - 返信不要の場合
- `info@example.com` - 一般的な問い合わせ
- `support@example.com` - サポート用
- `crm@example.com` - CRM専用

**重要**: このメールアドレスは実際に存在する必要はありません。SendGridが処理します。

### 複数のメールアドレスを使用する場合

Domain Authenticationを設定すれば、同じドメインの任意のメールアドレスから送信できます：

- `noreply@example.com`
- `info@example.com`
- `support@example.com`

すべて同じDomain Authentication設定で使用できます。

---

**これで、独自ドメインからメールが送信されるようになります！**
