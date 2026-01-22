# SendGrid SMTP設定の確認と修正

## 🔍 メール送信が失敗する原因

ログを見ると、SMTP接続がタイムアウトしています。これは以下の原因が考えられます：

1. **SendGridのSMTP設定が正しくない**
2. **環境変数が正しく設定されていない**
3. **SendGridのAPIキーが無効**
4. **ネットワーク接続の問題**

---

## 📋 SendGridの正しい設定

### Railway環境変数の確認

SendGridを使用する場合、以下の環境変数が正しく設定されている必要があります：

```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=katsuhiro.okazaki@bizcraft-studio.com
SMTP_FROM_NAME=CONNECT+ CRM
```

### 重要なポイント

1. **SMTP_SERVER**: `smtp.sendgrid.net`（SendGridのSMTPサーバー）
2. **SMTP_PORT**: `587`（STARTTLS）または `2525`（STARTTLS）
3. **SMTP_USERNAME**: `apikey`（固定値、必ずこの値）
4. **SMTP_PASSWORD**: SendGridのAPIキー（`SG.`で始まる文字列）
5. **SMTP_FROM_EMAIL**: 認証済みのメールアドレス（Single Sender VerificationまたはDomain Authenticationで認証済み）

---

## 🔧 設定手順

### ステップ1: SendGridのAPIキーを確認

1. **SendGridダッシュボードを開く**
   - https://app.sendgrid.com にアクセス
   - ログイン

2. **APIキーを確認**
   - 「Settings」→「API Keys」を選択
   - APIキーが作成されているか確認
   - もし作成されていない場合は、「Create API Key」をクリック
   - 名前を入力（例: "Railway SMTP"）
   - 権限: 「Full Access」または「Mail Send」を選択
   - 「Create & View」をクリック
   - **APIキーをコピー**（この時だけ表示されます）

### ステップ2: Single Sender Verificationを確認

1. **SendGridダッシュボードで「Settings」→「Sender Authentication」を選択**
2. **「Single Sender Verification」を確認**
   - `katsuhiro.okazaki@bizcraft-studio.com` が「Verified」になっているか確認
   - もし「Unverified」の場合は、メール認証を完了する

### ステップ3: Railwayの環境変数を設定

1. **Railwayダッシュボードを開く**
   - https://railway.app にアクセス
   - プロジェクトを選択
   - 「web」サービスを選択

2. **「Variables」タブを開く**

3. **以下の環境変数を設定/確認**

   ```
   SMTP_SERVER=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SMTP_FROM_EMAIL=katsuhiro.okazaki@bizcraft-studio.com
   SMTP_FROM_NAME=CONNECT+ CRM
   ```

   **注意:**
   - `SMTP_USERNAME` は必ず `apikey` と設定（固定値）
   - `SMTP_PASSWORD` はSendGridのAPIキー（`SG.`で始まる文字列）
   - `SMTP_FROM_EMAIL` は認証済みのメールアドレス

4. **「Deploy」をクリックして再デプロイ**

---

## 🔍 設定の確認方法

### 1. Railwayの環境変数を確認

1. Railwayダッシュボードで「Variables」タブを開く
2. 上記の環境変数が正しく設定されているか確認
3. 特に `SMTP_USERNAME` が `apikey` になっているか確認

### 2. SendGridのAPIキーを確認

1. SendGridダッシュボードで「Settings」→「API Keys」を選択
2. APIキーが作成されているか確認
3. APIキーの権限が「Full Access」または「Mail Send」になっているか確認

### 3. Single Sender Verificationを確認

1. SendGridダッシュボードで「Settings」→「Sender Authentication」を選択
2. 「Single Sender Verification」で `katsuhiro.okazaki@bizcraft-studio.com` が「Verified」になっているか確認

### 4. デプロイ後のログを確認

1. Railwayの「Deploy Logs」を開く
2. 2段階認証設定を試行
3. 以下のログを確認：
   - `[2FA Email] ポート 587 で接続中（タイムアウト: 5秒）...`
   - 成功: `[2FA Email] ✓ Code sent to ...`
   - 失敗: `[2FA Email] ポート 587 で接続エラー: ...` または `[2FA Email] ポート 587 でSMTP認証エラー: ...`

---

## ⚠️ よくある間違い

### 1. SMTP_USERNAMEが間違っている

**間違い:**
```
SMTP_USERNAME=katsuhiro.okazaki@bizcraft-studio.com
```

**正しい:**
```
SMTP_USERNAME=apikey
```

### 2. SMTP_PASSWORDが間違っている

**間違い:**
```
SMTP_PASSWORD=メールアドレスのパスワード
```

**正しい:**
```
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. SMTP_SERVERが間違っている

**間違い:**
```
SMTP_SERVER=smtp.gmail.com
SMTP_SERVER=mail.sendgrid.net
```

**正しい:**
```
SMTP_SERVER=smtp.sendgrid.net
```

### 4. SMTP_FROM_EMAILが認証されていない

- Single Sender VerificationまたはDomain Authenticationで認証されていないメールアドレスは使用できません
- SendGridダッシュボードで「Settings」→「Sender Authentication」を確認

---

## 🚀 次のステップ

1. **SendGridのAPIキーを確認/作成**
2. **Single Sender Verificationを確認**
3. **Railwayの環境変数を設定**
4. **再デプロイ**
5. **2段階認証設定を再試行**
6. **ログを確認して、メール送信が成功したか確認**

---

**まず、Railwayの環境変数が正しく設定されているか確認してください！**
