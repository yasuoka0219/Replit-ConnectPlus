# メール送信機能のデプロイ手順

## ✅ コミット完了

変更をコミットしました：
- メール送信機能の追加
- 2段階認証メール送信
- 連絡先へのメール送信機能
- 汎用メール送信ユーティリティ

---

## 🚀 デプロイ手順

### ステップ1: GitHubにプッシュ

ターミナルで以下を実行してください：

```bash
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
git push origin main
```

GitHubの認証情報を求められた場合は、入力してください。

---

### ステップ2: 本番環境の環境変数を設定

本番環境（Railway、Render、Herokuなど）で、以下の環境変数を設定してください：

#### Railwayの場合

1. Railwayダッシュボード → プロジェクト → 「Variables」
2. 以下の環境変数を追加：

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=0219ko@gmail.com
SMTP_PASSWORD=gfviqnlxdjdilfac
SMTP_FROM_EMAIL=0219ko@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

3. 「Deployments」→「Redeploy」

#### Renderの場合

1. Renderダッシュボード → サービス → 「Environment」
2. 以下の環境変数を追加：

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=0219ko@gmail.com
SMTP_PASSWORD=gfviqnlxdjdilfac
SMTP_FROM_EMAIL=0219ko@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

3. 「Manual Deploy」→「Deploy latest commit」

#### Herokuの場合

```bash
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USERNAME=0219ko@gmail.com
heroku config:set SMTP_PASSWORD=gfviqnlxdjdilfac
heroku config:set SMTP_FROM_EMAIL=0219ko@gmail.com
heroku config:set SMTP_FROM_NAME="CONNECT+ CRM"
heroku restart
```

---

### ステップ3: デプロイの確認

1. **デプロイの完了を待つ**
   - Railway/Render/Herokuのダッシュボードでデプロイ状況を確認
   - デプロイが完了するまで数分かかる場合があります

2. **アプリケーションにアクセス**
   - 本番環境のURLにアクセス
   - ログイン

3. **2段階認証メールの確認**
   - 「設定」→「2段階認証設定」を開く
   - 「2段階認証を設定する（メール認証）」をクリック
   - `0219ko@gmail.com` に認証コードが送信されるか確認

4. **連絡先へのメール送信の確認**
   - 企業詳細画面 → 「連絡先」タブ
   - 連絡先の「メール送信」ボタンをクリック
   - メール送信フォームが表示されるか確認

---

## 🔍 トラブルシューティング

### メールが届かない場合

1. **環境変数を確認**
   - 本番環境で環境変数が正しく設定されているか確認
   - `SMTP_USERNAME`と`SMTP_PASSWORD`が正しいか確認

2. **ログを確認**
   - Railway: `railway logs`
   - Render: ダッシュボードの「Logs」タブ
   - Heroku: `heroku logs --tail`
   - エラーメッセージがないか確認

3. **アプリケーションを再起動**
   - 環境変数を変更した後、アプリケーションを再起動

### デプロイが失敗する場合

1. **ビルドログを確認**
   - エラーメッセージを確認
   - 依存関係のインストールエラーがないか確認

2. **環境変数の確認**
   - 必須の環境変数（`DATABASE_URL`、`SESSION_SECRET`など）が設定されているか確認

---

## 📋 デプロイチェックリスト

- [ ] GitHubにプッシュ完了
- [ ] 本番環境の環境変数を設定（SMTP設定を含む）
- [ ] アプリケーションを再起動
- [ ] 2段階認証メールが届くか確認
- [ ] 連絡先へのメール送信が動作するか確認
- [ ] ログにエラーがないか確認

---

## 🎉 デプロイ完了後

以下の機能が利用可能になります：

- ✅ 2段階認証メール送信
- ✅ パスワードリセットメール送信
- ✅ 連絡先へのメール送信
- ✅ 活動履歴への自動記録

---

**重要**: `.env`ファイルはコミットされていません（`.gitignore`で除外）。本番環境では、必ず環境変数として設定してください。
