# Railway 環境変数の詳しい設定方法

Web サービスの **Variables** タブで、以下の変数を設定します。

---

## 1. DATABASE_URL（Variable Reference で参照）

Postgres の接続情報を、**参照**で渡します（値をコピペしなくてよい方法です）。

### 手順

1. Railway で **Web 用のサービス**（Empty Service で作った方）をクリック
2. **「Variables」** タブを開く
3. **「+ New Variable」** または **「Add Variable」** をクリック
4. **変数名:** `DATABASE_URL`
5. **値の入力欄**の右側や下に **「Reference」** や **「Add Reference」** のようなボタンがある場合:
   - それをクリック
   - **Service** で **「Postgres」** を選択
   - **Variable** で **「DATABASE_URL」** を選択
   - 保存
6. **Reference がない場合（値を直接入れる場合）:**
   - Postgres サービスを開く → **Variables** タブ
   - `DATABASE_URL` の値を **表示**（目のアイコンなど）してコピー
   - Web サービスの Variables に戻り、`DATABASE_URL` という名前で **貼り付け** して保存

### 参照する変数

- **参照元サービス:** Postgres  
- **参照する変数名:** `DATABASE_URL`  

※Postgres の Variables に `DATABASE_URL` と `DATABASE_PUBLIC_URL` がある場合は、**同じプロジェクト内の Web サービスから使うなら `DATABASE_URL`（内部用）を参照**してください。

---

## 2. SESSION_SECRET（長いランダム文字列）

セッションや Cookie の署名に使う秘密鍵です。**推測されない長いランダム文字列**にします。

### ターミナルで生成する方法（推奨）

1. ターミナル（Cursor のターミナルや Mac のターミナル）を開く
2. 次のコマンドを実行:

```bash
openssl rand -hex 32
```

3. 表示された **1行の英数字**（64文字）をコピー  
   例: `a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456`

### Railway での設定

1. Web サービスの **Variables** タブを開く
2. **「+ New Variable」** をクリック
3. **変数名:** `SESSION_SECRET`
4. **値:** さきほどコピーしたランダム文字列をそのまま貼り付け（前後にスペースを入れない）
5. 保存

### 注意

- 他人に教えたり、Git にコミットしたりしない
- 本番用は必ずこのようにランダムな値にする

---

## 3. SMTP 関連（SendGrid）

メール送信（2段階認証など）に使う設定です。**以前使っていた SendGrid の値**をそのまま使います。

### 変数一覧と値

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `SMTP_SERVER` | `smtp.sendgrid.net` | SendGrid の SMTP サーバー（固定） |
| `SMTP_PORT` | `587` または `2525` | 587 で問題なければ 587 |
| `SMTP_USERNAME` | `apikey` | **必ずこの文字列**（メールアドレスではない） |
| `SMTP_PASSWORD` | SendGrid の API キー | `SG.` で始まる長い文字列（SendGrid の API Keys で確認） |
| `SMTP_FROM_EMAIL` | 送信元メールアドレス | 例: `katsuhiro.okazaki@bizcraft-studio.com` |
| `SMTP_FROM_NAME` | 送信元の表示名 | 例: `CONNECT+ CRM` |

### 各項目の設定手順

#### SMTP_SERVER

1. **+ New Variable** で変数名 `SMTP_SERVER`
2. 値: `smtp.sendgrid.net` と入力
3. 保存

#### SMTP_PORT

1. 変数名: `SMTP_PORT`
2. 値: `587` または `2525`（どちらか1つ）
3. 保存

#### SMTP_USERNAME

1. 変数名: `SMTP_USERNAME`
2. 値: **半角で** `apikey` とだけ入力（メールアドレスは入れない）
3. 保存

#### SMTP_PASSWORD（SendGrid API キー）

1. SendGrid にログイン: https://app.sendgrid.com  
2. **Settings** → **API Keys** を開く  
3. 既存の API キーを使うか、**Create API Key** で新規作成  
4. 表示された API キー（`SG.` で始まる長い文字列）をコピー  
   - 新規作成時は **このときしか表示されない** ので必ずコピー  
5. Railway の Web サービス **Variables** で:  
   - 変数名: `SMTP_PASSWORD`  
   - 値: コピーした API キーを貼り付け（前後にスペースを入れない）  
6. 保存

#### SMTP_FROM_EMAIL

1. 変数名: `SMTP_FROM_EMAIL`
2. 値: SendGrid で認証済みの送信元アドレス  
   - 例: `katsuhiro.okazaki@bizcraft-studio.com`  
   - Single Sender Verification で認証したアドレスを使う
3. 保存

#### SMTP_FROM_NAME

1. 変数名: `SMTP_FROM_NAME`
2. 値: メールの「差出人」に表示する名前  
   - 例: `CONNECT+ CRM`
3. 保存

---

## 設定後の確認リスト

- [ ] `DATABASE_URL` … Postgres の `DATABASE_URL` を参照（またはコピー）
- [ ] `SESSION_SECRET` … `openssl rand -hex 32` で生成した値を設定
- [ ] `SMTP_SERVER` … `smtp.sendgrid.net`
- [ ] `SMTP_PORT` … `587` または `2525`
- [ ] `SMTP_USERNAME` … `apikey`
- [ ] `SMTP_PASSWORD` … SendGrid の API キー（`SG.` で始まる）
- [ ] `SMTP_FROM_EMAIL` … 認証済みの送信元メールアドレス
- [ ] `SMTP_FROM_NAME` … 送信元の表示名（例: `CONNECT+ CRM`）

---

## 補足

- **Variable Reference** を使うと、Postgres の接続情報が変わっても Web サービス側を書き換えずに済みます。
- **SESSION_SECRET** は本番では必ずランダムな値にしてください。
- **SMTP_USERNAME** は SendGrid では常に `apikey` です（メールアドレスではありません）。

設定後、**Deployments** で再デプロイされるか、**railway up** でデプロイし直すと反映されます。
