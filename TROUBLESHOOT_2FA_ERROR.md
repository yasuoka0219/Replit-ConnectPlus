# 2段階認証エラーのトラブルシューティング

## 🔴 発生しているエラー

「エラー: サーバーエラーが発生しました。ログを確認してください。」

このエラーは、2段階認証設定時にメール送信で問題が発生している可能性が高いです。

---

## 🔍 ステップ1: Railwayのログを確認

### ログの確認方法

1. **Railwayダッシュボードを開く**
   - https://railway.app にアクセス
   - プロジェクトを選択
   - 「web」サービスを選択

2. **「HTTP Logs」タブを開く**
   - 左サイドバーまたは上部のタブから「HTTP Logs」を選択
   - リアルタイムのログが表示されます

3. **エラーログを確認**
   - `[2FA Email]` で始まるログを探す
   - エラーメッセージの詳細を確認

### 確認すべきログ

以下のようなログを探してください：

```
[2FA Email] 試行 1/3: ポート 587 で接続中...
[2FA Email] ❌ SMTP認証エラー: ...
[2FA Email] ❌ SMTPエラー: ...
[2FA Email] ❌ 予期しないエラー: ...
```

---

## 🔧 よくある原因と解決方法

### 原因1: SendGridのAPIキーが正しく設定されていない

**確認方法:**
- Railwayダッシュボード → 「Variables」
- `SMTP_PASSWORD` の値を確認
- SendGridのAPIキーが正しく設定されているか確認

**解決方法:**
1. SendGridダッシュボード → 「Settings」→「API Keys」
2. APIキーを再生成（必要に応じて）
3. Railwayで `SMTP_PASSWORD` を更新
4. 再デプロイ

### 原因2: SMTP設定が正しくない

**確認方法:**
- Railwayダッシュボード → 「Variables」
- 以下の環境変数が正しく設定されているか確認：

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxx...（SendGridのAPIキー）
SMTP_FROM_EMAIL=noreply@bizcraft-studio.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**解決方法:**
- 環境変数を再確認
- `SMTP_USERNAME` が `apikey` になっているか確認
- `SMTP_PASSWORD` にAPIキー全体が設定されているか確認

### 原因3: Domain Authenticationが完了していない

**確認方法:**
- SendGridダッシュボード → 「Settings」→「Sender Authentication」
- `bizcraft-studio.com` が「Verified」になっているか確認

**解決方法:**
- Domain Authenticationが完了していない場合は、完了させる
- CNAMEレコードが正しく設定されているか確認

### 原因4: データベースのマイグレーションが不足

**確認方法:**
- Railwayのログで `Email2FACode` テーブルに関するエラーがないか確認

**解決方法:**
- マイグレーションを実行（通常は自動で実行されますが、必要に応じて手動で実行）

---

## 🛠️ 即座に試せる対処法

### 方法1: 環境変数を再確認

1. Railwayダッシュボード → 「Variables」
2. すべてのSMTP関連の環境変数を確認
3. 誤りがあれば修正
4. 再デプロイ

### 方法2: SendGridのAPIキーを再生成

1. SendGridダッシュボード → 「Settings」→「API Keys」
2. 既存のAPIキーを削除（必要に応じて）
3. 新しいAPIキーを生成
4. Railwayで `SMTP_PASSWORD` を更新
5. 再デプロイ

### 方法3: ログから認証コードを確認

メール送信に失敗しても、ログに認証コードが表示される場合があります：

1. Railwayダッシュボード → 「HTTP Logs」
2. `[2FA Email] 認証コード:` で始まるログを探す
3. 認証コードをコピー
4. 2段階認証設定画面で認証コードを入力

---

## 📋 チェックリスト

- [ ] Railwayの「HTTP Logs」でエラーログを確認
- [ ] `SMTP_PASSWORD` が正しく設定されているか確認
- [ ] `SMTP_USERNAME` が `apikey` になっているか確認
- [ ] SendGridのDomain Authenticationが「Verified」になっているか確認
- [ ] 環境変数を再確認
- [ ] 再デプロイ
- [ ] 再度2段階認証設定を試す

---

## 💡 ログの共有

エラーの詳細を確認するために、Railwayの「HTTP Logs」で以下の情報を確認してください：

1. **エラーメッセージの全文**
2. **`[2FA Email]` で始まるログ**
3. **スタックトレース（エラーの詳細）**

これらの情報があれば、より具体的な解決方法を提案できます。

---

**まず、Railwayの「HTTP Logs」でエラーログを確認してください！**
