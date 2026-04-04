# Railway CLI でデプロイする方法（GitHub 連携ができない場合）

## 概要

GitHub のリポジトリが Railway に表示されない場合、**Railway CLI** を使って、ローカルのフォルダから直接デプロイできます。

---

## 前提

- プロジェクト **clever-ambition** に **Postgres** はある
- **Web 用のサービス** を CLI で追加して、そこにデプロイする

---

## 手順

### ステップ1: Railway で「空のサービス」を追加する

1. Railway ダッシュボードを開く
2. プロジェクト **clever-ambition** を開く
3. 左の **「+」** または **「New」** をクリック
4. メニューから次のいずれかを探して選択：
   - **「Empty Service」**
   - **「Empty」**
   - **「Deploy from CLI」** や **「Local」** など、GitHub 以外のデプロイ方法
5. サービスが1つ追加される（名前は後で変えられる場合あり）
6. 追加されたサービスをクリックし、**Settings** で名前を **web** などにしておくと分かりやすい

※「Empty Service」が無い場合は、**ステップ2** の `railway init` で新規サービスを作る方法に進んでください。

---

### ステップ2: Railway CLI をインストール

**macOS（Homebrew）:**

```bash
brew install railway
```

**その他（npm）:**

```bash
npm install -g @railway/cli
```

または公式のインストール方法:  
https://docs.railway.app/develop/cli

---

### ステップ3: ログインとプロジェクトの紐付け

1. ターミナルでプロジェクトのフォルダに移動:

```bash
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
```

2. ログイン:

```bash
railway login
```

ブラウザが開くので、Railway にログインしてください。

3. プロジェクト・サービスに紐付け:

```bash
railway link
```

- プロジェクト一覧で **clever-ambition** を選択
- サービス一覧で、**ステップ1で作った Web 用のサービス**（または Postgres 以外のサービス）を選択

※`railway link` でサービスを選べない場合は、先にダッシュボードで「Empty Service」を追加してから再度 `railway link` を実行してください。

---

### ステップ4: 環境変数を設定する

**方法A: ダッシュボードで設定（推奨）**

1. Railway で **Web 用のサービス** を開く
2. **Variables** タブを開く
3. 以下を追加・編集：

| 変数名 | 値 |
|--------|-----|
| `DATABASE_URL` | Postgres の Variables にある `DATABASE_URL` を **Variable Reference** で参照（または値をコピー） |
| `SESSION_SECRET` | ランダムな長い文字列（例: ターミナルで `openssl rand -hex 32` を実行して表示された値） |
| `SMTP_SERVER` | `smtp.sendgrid.net` |
| `SMTP_PORT` | `587` または `2525` |
| `SMTP_USERNAME` | `apikey` |
| `SMTP_PASSWORD` | SendGrid の API キー |
| `SMTP_FROM_EMAIL` | 送信元メールアドレス |
| `SMTP_FROM_NAME` | `CONNECT+ CRM` |

**方法B: CLI で設定**

```bash
railway variables set SESSION_SECRET="ここにランダムな文字列"
railway variables set SMTP_SERVER="smtp.sendgrid.net"
# ... 他の変数も同様
```

`DATABASE_URL` は Postgres の値を参照する必要があるため、**方法A（ダッシュボードの Variable Reference）** が確実です。

---

### ステップ5: デプロイする

プロジェクトのフォルダで:

```bash
railway up
```

アップロードとビルドが始まります。完了後、Railway の **Deployments** タブで成功しているか確認してください。

---

### ステップ6: ドメイン（URL）を発行する

1. Railway で **Web 用のサービス** を開く
2. **Settings** → **Networking**（または **Domains**）
3. **「Generate Domain」** をクリック
4. 表示された URL（例: `xxxxx.up.railway.app`）でサイトにアクセス

---

## うまくいかないとき

- **「No project linked」** と出る → `railway link` で clever-ambition と Web 用サービスを選び直す
- **ビルドエラー** → そのサービスの **Deploy Logs** を開き、表示されたエラーに合わせて修正
- **DATABASE_URL が無い** → Web 用サービスの Variables で、Postgres の `DATABASE_URL` を Variable Reference で参照する

---

## まとめ

1. Railway で **Empty Service**（Web 用）を追加  
2. **railway login** → **railway link**（clever-ambition ＋ そのサービス）  
3. Web 用サービスの **Variables** で `DATABASE_URL` などを設定  
4. **railway up** でデプロイ  
5. **Generate Domain** で URL を発行  

これで GitHub 連携なしで、ローカルから同じプロジェクト（clever-ambition）にデプロイできます。
