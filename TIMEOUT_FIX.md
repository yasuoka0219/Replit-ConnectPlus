# タイムアウト問題の修正

## 🔧 実施した修正

### 問題
- SMTP接続がタイムアウトし、Gunicornワーカータイムアウト（30秒）を超えていた
- ポート587でタイムアウト後、ポート465でも試行していたが、それもタイムアウトしていた
- リトライと待機時間により、処理時間が30秒を超えていた

### 修正内容

1. **タイムアウトを5秒に短縮**
   - `connection_timeout = 10` → `connection_timeout = 5`
   - より早く失敗を検出し、ワーカータイムアウトを避ける

2. **リトライを削除**
   - `max_retries = 2` → リトライなし（最初の試行のみ）
   - 待機時間（`time.sleep()`）を削除

3. **ポートフォールバックを削除**
   - ポート587と465の両方を試行していた処理を削除
   - 設定されたポートのみ試行（通常は587）

### 修正したファイル

- `utils/email_2fa.py` - 2段階認証メール送信
- `utils/email_sender.py` - 汎用メール送信
- `utils/password_reset.py` - パスワードリセットメール送信

---

## 📋 SendGridの設定確認

SendGridを使用している場合、以下の環境変数が正しく設定されているか確認してください：

### Railway環境変数

```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=katsuhiro.okazaki@bizcraft-studio.com
SMTP_FROM_NAME=CONNECT+ CRM
```

### 重要なポイント

1. **SMTP_USERNAME**: `apikey` と設定（固定値）
2. **SMTP_PASSWORD**: SendGridのAPIキー（`SG.`で始まる文字列）
3. **SMTP_SERVER**: `smtp.sendgrid.net`（SendGridのSMTPサーバー）
4. **SMTP_PORT**: `587`（STARTTLS）または `2525`（STARTTLS）

---

## 🔍 確認方法

### 1. Railwayの環境変数を確認

1. Railwayダッシュボードを開く
2. プロジェクトを選択
3. 「web」サービスを選択
4. 「Variables」タブを開く
5. 上記の環境変数が正しく設定されているか確認

### 2. SendGridのAPIキーを確認

1. SendGridダッシュボードを開く
2. 「Settings」→「API Keys」を選択
3. APIキーが作成されているか確認
4. APIキーをコピーして、Railwayの`SMTP_PASSWORD`に設定

### 3. デプロイ後のログを確認

1. Railwayの「Deploy Logs」を開く
2. 2段階認証設定を試行
3. 以下のログを確認：
   - `[2FA Email] ポート 587 で接続中（タイムアウト: 5秒）...`
   - 成功: `[2FA Email] ✓ Code sent to ...`
   - 失敗: `[2FA Email] ポート 587 で接続エラー: ...`

---

## ⚠️ 注意事項

### タイムアウトが短い理由

- Gunicornのワーカータイムアウトは通常30秒
- 5秒のタイムアウトでも、接続が確立できない場合は即座に失敗する
- これにより、ワーカータイムアウトを避け、ユーザーにエラーメッセージを表示できる

### メールが届かない場合

1. **認証コードはログに表示されます**
   - Railwayの「HTTP Logs」で `認証コード` と検索
   - ログから認証コードを確認して、2段階認証を設定できます

2. **SendGridの設定を確認**
   - APIキーが正しいか
   - ドメイン認証が完了しているか
   - Single Sender Verificationが完了しているか

3. **ネットワーク接続を確認**
   - RailwayからSendGridへの接続が可能か
   - ファイアウォールやセキュリティグループの設定を確認

---

## 🚀 次のステップ

1. **コードをGitHubにプッシュ**
   ```bash
   git add .
   git commit -m "Fix: Reduce SMTP timeout to 5 seconds to avoid worker timeout"
   git push origin main
   ```

2. **Railwayで自動デプロイを確認**
   - Railwayが自動的にデプロイを開始します
   - 「Deploy Logs」でデプロイの進行状況を確認

3. **2段階認証設定を再試行**
   - デプロイ完了後、2段階認証設定を再試行
   - ログを確認して、エラーが解消されたか確認

---

**修正が完了しました。GitHubにプッシュして、Railwayでデプロイしてください！**
