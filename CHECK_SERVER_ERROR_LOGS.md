# サーバーエラーのログ確認方法

## 🔍 ステップ1: Railwayのログを確認

### ログの確認方法

1. **Railwayダッシュボードを開く**
   - https://railway.app にアクセス
   - プロジェクトを選択
   - 「web」サービスを選択

2. **「HTTP Logs」タブを開く**
   - 左サイドバーまたは上部のタブから「HTTP Logs」を選択

3. **検索バーで検索**
   - 検索バーに `[2FA` と入力
   - または、`error` と入力してエラーログを探す

4. **ログを確認**
   - エラーメッセージの全文を確認
   - スタックトレース（エラーの詳細）を確認

---

## 🔍 ステップ2: 確認すべきログ

### メール送信の試行ログ

以下のようなログを探してください：

```
[2FA Email] 試行 1/2: ポート 587 で接続中...
[2FA Email] ポート 587 で接続エラー: ...
[2FA Email] ❌ SMTP認証エラー: ...
[2FA Email] ❌ SMTPエラー: ...
[2FA Email] ❌ すべての試行が失敗しました。最後のエラー: ...
```

### 認証コードのログ

メール送信に失敗しても、ログに認証コードが表示される場合があります：

```
[2FA Setup] 認証コード（ログから確認）: 123456
[2FA Email] 認証コード: 123456
```

---

## 🔧 よくある原因と解決方法

### 原因1: SMTP認証エラー

**ログに表示されるエラー:**
```
[2FA Email] ❌ SMTP認証エラー: ...
```

**確認方法:**
1. Railwayダッシュボード → 「Variables」
2. `SMTP_USERNAME` が `apikey` になっているか確認
3. `SMTP_PASSWORD` にSendGridのAPIキーが正しく設定されているか確認

**解決方法:**
1. SendGridダッシュボード → 「Settings」→「API Keys」
2. APIキーを確認
3. Railwayで `SMTP_PASSWORD` を更新
4. 再デプロイ

### 原因2: SMTP接続エラー

**ログに表示されるエラー:**
```
[2FA Email] ポート 587 で接続エラー: ...
```

**確認方法:**
1. Railwayダッシュボード → 「Variables」
2. `SMTP_SERVER` が `smtp.sendgrid.net` になっているか確認
3. `SMTP_PORT` が `587` または `465` になっているか確認

**解決方法:**
1. ポートを変更してみる：
   - `SMTP_PORT=587` → `SMTP_PORT=465` に変更
   - または、その逆
2. 保存して再デプロイ

### 原因3: タイムアウトエラー

**ログに表示されるエラー:**
```
[2FA Email] ポート 587 で接続エラー: timeout
```

**解決方法:**
- タイムアウトは既に10秒に短縮済み
- ポート465を試す

---

## 🛠️ 即座に試せる対処法

### 方法1: ログから認証コードを確認

メール送信に失敗しても、ログに認証コードが表示される場合があります：

1. Railwayダッシュボード → 「HTTP Logs」
2. 検索バーに `認証コード` と入力
3. `[2FA Setup] 認証コード（ログから確認）:` で始まるログを探す
4. 認証コードをコピー
5. 2段階認証設定画面で認証コードを入力

### 方法2: 環境変数を再確認

1. Railwayダッシュボード → 「Variables」
2. すべてのSMTP関連の環境変数を確認：

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxx...（SendGridのAPIキー）
SMTP_FROM_EMAIL=noreply@bizcraft-studio.com
SMTP_FROM_NAME=CONNECT+ CRM
```

3. 誤りがあれば修正
4. 再デプロイ

### 方法3: ポートを変更してみる

1. Railwayダッシュボード → 「Variables」
2. `SMTP_PORT` を `587` から `465` に変更
3. 保存
4. 再デプロイ
5. 再度2段階認証設定を試す

---

## 📋 チェックリスト

- [ ] Railwayの「HTTP Logs」で `[2FA` と検索
- [ ] エラーメッセージの全文を確認
- [ ] ログから認証コードを確認（メール送信に失敗した場合）
- [ ] `SMTP_USERNAME` が `apikey` になっているか確認
- [ ] `SMTP_PASSWORD` にSendGridのAPIキーが正しく設定されているか確認
- [ ] `SMTP_SERVER` が `smtp.sendgrid.net` になっているか確認
- [ ] `SMTP_PORT` が `587` または `465` になっているか確認
- [ ] SendGridのDomain Authenticationが「Verified」になっているか確認

---

## 💡 ログの共有

エラーの詳細を確認するために、Railwayの「HTTP Logs」で以下の情報を確認してください：

1. **エラーメッセージの全文**
2. **`[2FA Email]` で始まるログ**
3. **`[2FA Setup]` で始まるログ**
4. **認証コードが表示されているログ**

これらの情報があれば、より具体的な解決方法を提案できます。

---

**まず、Railwayの「HTTP Logs」で `[2FA` と検索して、エラーログと認証コードを確認してください！**
