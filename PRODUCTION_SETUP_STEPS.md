# 本番環境でサイトを表示する手順

## 現状

- **Connect-plus**: オフライン
- **Postgres**: クラッシュ（2日前）

サイトを表示するには、Postgres を復旧し、Connect-plus をデプロイしてドメインでアクセスできるようにします。

---

## 手順一覧

1. Postgres を再起動する
2. Connect-plus の環境変数を確認する
3. Connect-plus をデプロイする
4. ドメインを発行する
5. サイトにアクセスする

---

## ステップ1: Postgres を再起動する

1. Railway ダッシュボードを開く
2. 左の **「Postgres」** をクリック
3. **「Deployments」** タブを開く
4. いちばん上（ACTIVE または直近）のデプロイの **「⋯」**（3点メニュー）をクリック
5. **「Redeploy」** を選択
6. 1〜2分待ち、Postgres が **緑の「Online」** になるか確認

**Redeploy が無い場合**

- **「Settings」** タブ → **「Redeploy」** や **「Restart」** のボタンがないか確認
- それでも復旧しない場合は、**新規で Postgres を追加**し、Connect-plus の `DATABASE_URL` を新しい Postgres の値に変更する必要があります

---

## ステップ2: Connect-plus の環境変数を確認する

1. 左の **「Connect-plus」** をクリック
2. **「Variables」** タブを開く
3. 次の変数がすべてあるか確認

| 変数名 | 内容 |
|--------|------|
| **DATABASE_URL** | Postgres の `DATABASE_URL` を Reference で参照（必須） |
| **SESSION_SECRET** | 長いランダム文字列（必須） |
| **SMTP_SERVER** | `smtp.sendgrid.net` |
| **SMTP_PORT** | `587` または `2525` |
| **SMTP_USERNAME** | `apikey` |
| **SMTP_PASSWORD** | SendGrid の API キー |
| **SMTP_FROM_EMAIL** | 送信元メールアドレス |
| **SMTP_FROM_NAME** | `CONNECT+ CRM` |

**DATABASE_URL が無い場合**

1. **「Add Variable」** または紫色の **「Add Variable」** をクリック
2. 変数名: `DATABASE_URL`
3. 値: **Variable Reference** で **Postgres** の **DATABASE_URL** を選択して保存

---

## ステップ3: Connect-plus をデプロイする

**方法A: Railway の画面から**

1. **Connect-plus** を開いたまま **「Deployments」** タブを開く
2. 最新のデプロイの **「⋯」** → **「Redeploy」** をクリック
3. ビルド・デプロイが完了するまで待つ（2〜5分程度）
4. ステータスが **「Success」** になり、サービスが **「Online」** になるか確認

**方法B: ローカルから CLI で**

1. ターミナルでプロジェクトフォルダに移動:
   ```bash
   cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
   ```
2. Railway にログイン・プロジェクト紐付け済みなら:
   ```bash
   railway up
   ```
3. アップロード・デプロイが完了するまで待つ

---

## ステップ4: ドメインを発行する

1. **Connect-plus** の **「Settings」** タブを開く
2. **「Networking」**（または **「Domains」**）を開く
3. **「Generate Domain」** をクリック
4. ポートに **8080** が入っているか確認し、**「Generate Domain」** を実行
5. 表示された URL（例: `connectplus-production.up.railway.app`）をメモ

---

## ステップ5: サイトにアクセスする

1. ブラウザで **https://（表示されたドメイン）** を開く  
   例: `https://connectplus-production.up.railway.app`
2. ログイン画面が表示されれば本番環境で確認できています
3. データベースは新規のため、**新規ユーザー登録** から利用を開始します

---

## トラブルシューティング

### Postgres が Online にならない

- **Deployments** の **View logs** でエラー内容を確認
- 復旧しない場合は、**新規 Postgres** を追加し、Connect-plus の `DATABASE_URL` を新しい Postgres の値に変更

### Connect-plus のデプロイが失敗する

- **Deploy Logs** でエラーメッセージを確認
- `DATABASE_URL` が正しく設定されているか再確認
- Postgres が **Online** の状態で再デプロイする

### ドメインで「Not Found」になる

- Connect-plus が **Online** か確認
- **Settings** → **Networking** で、ポート **8080** でドメインが発行されているか確認
- 数分待ってから再度アクセスする

---

## チェックリスト

- [ ] Postgres を Redeploy して Online にした
- [ ] Connect-plus の Variables に DATABASE_URL を設定した
- [ ] Connect-plus を Redeploy した（または railway up）
- [ ] デプロイが Success になり、サービスが Online になった
- [ ] Networking でドメインを発行した
- [ ] https://（ドメイン） でサイトにアクセスした

この順番で進めると、本番環境でサイトを確認できるようになります。
