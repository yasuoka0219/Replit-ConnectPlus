# SendGrid登録と設定ガイド

## ✅ 概要

SendGridに登録し、独自ドメイン（`bizcraft-studio.com`）からメールを送信できるように設定します。

**使用するドメイン:** `bizcraft-studio.com`

---

## 🚀 ステップ1: SendGridアカウント作成（約5分）

### 1-1. SendGridにアクセス

1. **SendGridのサイトにアクセス**
   - 日本版: https://sendgrid.kke.co.jp
   - または、グローバル版: https://sendgrid.com
   - **推奨**: グローバル版（https://sendgrid.com）を使用

2. **「Sign Up」をクリック**
   - トップページの「Sign Up」または「無料で始める」ボタンをクリック

### 1-2. アカウント情報を入力

1. **基本情報を入力**
   - **Email**: 会社のメールアドレス（例: `katsuhiro.okazaki@bizcraft-studio.com`）
   - **Password**: 強力なパスワードを設定
   - **Company Name**: 会社名（例: `BizCraft Studio`）

2. **利用規約に同意**
   - 「I agree to the Terms of Service and Privacy Policy」にチェック

3. **「Create Account」をクリック**
   - アカウントが作成されます

### 1-3. メール確認

1. **確認メールを確認**
   - 登録したメールアドレスに確認メールが届きます
   - メール内のリンクをクリックして確認

2. **アカウントが有効化されます**

---

## 🔐 ステップ2: Domain Authenticationの設定（約15分）

### 2-1. SendGridダッシュボードにログイン

1. **SendGridダッシュボードにアクセス**
   - https://app.sendgrid.com にアクセス
   - ログイン

2. **ダッシュボードを確認**
   - 初回ログイン時は、オンボーディング画面が表示される場合があります
   - 「Skip」または「Next」をクリックして進めます

### 2-2. Domain Authenticationを設定

1. **Sender Authenticationにアクセス**
   - 左メニュー → 「Settings」→「Sender Authentication」
   - または、直接: https://app.sendgrid.com/settings/sender_auth

2. **「Authenticate Your Domain」をクリック**
   - 「Authenticate Your Domain」ボタンをクリック
   - **注意**: 「Single Sender Verification」ではなく、「Domain Authentication」を選択

3. **ドメインを入力**
   - **Domain**: `bizcraft-studio.com`（サブドメインではなく、ルートドメイン）
   - **Subdomain**: 空欄のまま（使用しない）
   - 「Next」をクリック

4. **DNSレコードを確認**
   - SendGridが生成したDNSレコードが表示されます
   - 以下のようなCNAMEレコードが表示されます：
     ```
     Type: CNAME
     Host: em1234.bizcraft-studio.com
     Value: u1234567.wl123.sendgrid.net
     
     Type: CNAME
     Host: s1._domainkey.bizcraft-studio.com
     Value: s1.domainkey.u1234567.wl123.sendgrid.net
     
     Type: CNAME
     Host: s2._domainkey.bizcraft-studio.com
     Value: s2.domainkey.u1234567.wl123.sendgrid.net
     ```
   - **重要**: これらのレコードをコピーしておく

---

## 🌐 ステップ3: DNSレコードを追加（約10分）

### 3-1. ConoHaでDNS設定を開く

1. **ConoHaコントロールパネルにログイン**
   - https://www.conoha.jp/ にアクセス
   - コントロールパネルにログイン

2. **ドメイン管理にアクセス**
   - 上部のサービスアイコンから「VPS」をクリック
   - 左サイドバー → 「ドメイン」→「ドメイン」を選択

3. **ドメインを選択**
   - `bizcraft-studio.com` を選択
   - 「DNS設定」または「DNSレコード設定」を開く

### 3-2. CNAMEレコードを追加

1. **CNAMEレコードを追加**
   - 「レコード追加」または「+ 追加」ボタンをクリック

2. **SendGridで表示されたCNAMEレコードを追加**
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

3. **すべてのCNAMEレコードを追加**
   - SendGridで表示されたすべてのCNAMEレコードを追加
   - 通常、3〜4個のCNAMEレコードがあります

4. **保存**
   - 各レコードを保存

### 3-3. DNSの反映を待つ

1. **DNSの反映を待つ**
   - 通常、数分〜数時間かかります
   - 最大48時間かかる場合があります

2. **DNSの反映を確認（オプション）**
   - コマンドラインで確認：
     ```bash
     nslookup em1234.bizcraft-studio.com
     nslookup s1._domainkey.bizcraft-studio.com
     nslookup s2._domainkey.bizcraft-studio.com
     ```

---

## ✅ ステップ4: Domain Authenticationの確認（約5分）

### 4-1. SendGridダッシュボードに戻る

1. **Sender Authenticationにアクセス**
   - SendGridダッシュボード → 「Settings」→「Sender Authentication」
   - 設定したドメイン（`bizcraft-studio.com`）を選択

2. **「Verify」をクリック**
   - SendGridがDNSレコードを確認します
   - すべてのレコードが正しく設定されていれば「Verified」と表示されます

3. **確認が完了するまで待つ**
   - すべてのレコードが確認されるまで数分かかる場合があります
   - 「Verified」と表示されるまで待ちます

---

## 🔑 ステップ5: APIキーの生成（約2分）

### 5-1. APIキーを作成

1. **API Keysにアクセス**
   - 左メニュー → 「Settings」→「API Keys」
   - または、直接: https://app.sendgrid.com/settings/api_keys

2. **「Create API Key」をクリック**
   - 「Create API Key」ボタンをクリック

3. **APIキー情報を入力**
   - **API Key Name**: `CONNECT+ CRM`
   - **API Key Permissions**: 「Full Access」を選択
   - 「Create & View」をクリック

4. **APIキーをコピー**
   - **重要**: この画面でしか表示されません！
   - APIキーをコピー（例: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
   - 安全な場所に保存

---

## 🚂 ステップ6: Railwayで環境変数を設定（約2分）

### 6-1. Railwayダッシュボードを開く

1. **Railwayにアクセス**
   - https://railway.app にアクセス
   - ログイン

2. **プロジェクトを選択**
   - 使用しているプロジェクトを選択

3. **「web」サービスを選択**
   - サービス一覧から「web」を選択

### 6-2. 環境変数を設定

1. **「Variables」タブを開く**
   - 左サイドバーまたは上部のタブから「Variables」を選択

2. **環境変数を追加/更新**
   - 以下の環境変数を設定：

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=noreply@bizcraft-studio.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**重要:**
- `SMTP_USERNAME`は必ず`apikey`（そのまま）
- `SMTP_PASSWORD`には生成したAPIキー全体を貼り付け（`SG.`で始まる文字列）
- `SMTP_FROM_EMAIL`は独自ドメインのメールアドレス（例: `noreply@bizcraft-studio.com`）
  - このメールアドレスは実際に存在する必要はありません（SendGridが処理します）

3. **環境変数を保存**
   - 各環境変数を入力後、「Add」または「Save」をクリック
   - すべての環境変数が追加されるまで繰り返し

### 6-3. 再デプロイ

1. **「Deployments」タブを開く**
   - 左サイドバーまたは上部のタブから「Deployments」を選択

2. **「Redeploy」をクリック**
   - 最新のデプロイを選択
   - 「Redeploy」ボタンをクリック
   - または、環境変数を保存すると自動的に再デプロイが開始される場合があります

3. **デプロイの完了を待つ**
   - 通常、数分かかります

---

## 🧪 ステップ7: 動作確認（約2分）

### 7-1. アプリケーションにアクセス

1. **アプリケーションにアクセス**
   - RailwayのURLにアクセス
   - ログイン

2. **2段階認証を設定**
   - 「設定」→「2段階認証設定」
   - 「2段階認証を設定する（メール認証）」をクリック

3. **メールを確認**
   - 設定したメールアドレス（例: `noreply@bizcraft-studio.com`）から認証コードが届くことを確認
   - 認証コードを入力して2段階認証を有効化

✅ **完了！** SendGridを使用して独自ドメインからメールが正常に送信されるようになりました。

---

## 🔍 トラブルシューティング

### DNSレコードが反映されない場合

1. **DNSの反映を確認**
   - コマンドラインで確認：
     ```bash
     nslookup em1234.bizcraft-studio.com
     ```

2. **DNS設定を再確認**
   - ConoHaのDNS設定画面でCNAMEレコードが正しく設定されているか確認
   - タイポがないか確認

3. **時間を置いて再試行**
   - DNSの反映には時間がかかります
   - 数時間待ってから再度「Verify」をクリック

### Domain Authenticationが確認できない場合

1. **すべてのCNAMEレコードが設定されているか確認**
   - SendGridで表示されたすべてのレコードを追加する必要があります

2. **ドメイン名の入力ミスを確認**
   - サブドメインではなく、ルートドメイン（`bizcraft-studio.com`）を使用しているか確認

3. **SendGridサポートに問い合わせ**
   - 問題が解決しない場合は、SendGridサポートに問い合わせ

### メールが届かない場合

1. **環境変数を確認**
   - Railwayダッシュボード → 「Variables」
   - `SMTP_USERNAME=apikey`になっているか確認
   - `SMTP_PASSWORD`にAPIキーが正しく設定されているか確認

2. **SendGridで確認**
   - SendGridダッシュボード → 「Activity」
   - メール送信の履歴を確認
   - エラーがある場合は詳細を確認

3. **ログを確認**
   - Railwayダッシュボード → 「HTTP Logs」
   - `[2FA Email]`で始まるログを確認

---

## 📋 チェックリスト

- [ ] SendGridアカウントを作成
- [ ] メール確認を完了
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

- `noreply@bizcraft-studio.com` - 返信不要の場合
- `info@bizcraft-studio.com` - 一般的な問い合わせ
- `support@bizcraft-studio.com` - サポート用
- `crm@bizcraft-studio.com` - CRM専用

**重要**: このメールアドレスは実際に存在する必要はありません。SendGridが処理します。

### 複数のメールアドレスを使用する場合

Domain Authenticationを設定すれば、同じドメインの任意のメールアドレスから送信できます：

- `noreply@bizcraft-studio.com`
- `info@bizcraft-studio.com`
- `support@bizcraft-studio.com`

すべて同じDomain Authentication設定で使用できます。

### 無料プランの制限

- **送信数**: 1日100通まで
- **用途**: 2段階認証、パスワードリセット、お問い合わせなど
- **十分**: 小規模なCRM運用には十分

---

**これで、SendGridを使用して独自ドメインからメールが送信されるようになります！**
