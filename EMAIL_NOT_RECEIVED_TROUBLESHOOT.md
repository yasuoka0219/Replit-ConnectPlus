# メールが届かない場合のトラブルシューティング

## 🔍 ステップ1: Railwayのログを確認

### ログの確認方法

1. **Railwayダッシュボードを開く**
   - https://railway.app にアクセス
   - プロジェクトを選択
   - 「web」サービスを選択

2. **「HTTP Logs」タブを開く**
   - 左サイドバーまたは上部のタブから「HTTP Logs」を選択

3. **検索バーで検索**
   - 検索バーに `[2FA Email]` と入力
   - または、`[2FA Setup]` と入力

4. **ログを確認**
   - メール送信の試行ログを確認
   - エラーメッセージがないか確認

---

## 🔍 ステップ2: 確認すべきログ

### 正常な場合

```
[2FA Email] 試行 1/2: ポート 587 で接続中...
[2FA Email] ✓ Code sent to xxx@example.com (ポート 587)
```

### エラーの場合

以下のようなエラーログを探してください：

```
[2FA Email] 試行 1/2: ポート 587 で接続中...
[2FA Email] ポート 587 で接続エラー: ...
[2FA Email] ❌ SMTP認証エラー: ...
[2FA Email] ❌ SMTPエラー: ...
[2FA Email] ❌ すべての試行が失敗しました。最後のエラー: ...
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

### 原因3: Domain Authenticationが完了していない

**確認方法:**
1. SendGridダッシュボード → 「Settings」→「Sender Authentication」
2. `bizcraft-studio.com` が「Verified」になっているか確認

**解決方法:**
- Domain Authenticationが完了していない場合は、完了させる
- CNAMEレコードが正しく設定されているか確認

### 原因4: 送信元メールアドレスが正しくない

**確認方法:**
1. Railwayダッシュボード → 「Variables」
2. `SMTP_FROM_EMAIL` が `noreply@bizcraft-studio.com` になっているか確認

**解決方法:**
- `SMTP_FROM_EMAIL` を正しいメールアドレスに設定
- Domain Authenticationで認証されたドメインのメールアドレスを使用

### 原因5: メールがスパムフォルダに入っている

**確認方法:**
1. メールボックスのスパムフォルダを確認
2. 迷惑メールフォルダを確認

**解決方法:**
- スパムフォルダからメールを見つけて、通常のフォルダに移動
- 送信元メールアドレスを「安全な送信元」として登録

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

- [ ] Railwayの「HTTP Logs」で `[2FA Email]` を検索
- [ ] エラーメッセージの全文を確認
- [ ] `SMTP_USERNAME` が `apikey` になっているか確認
- [ ] `SMTP_PASSWORD` にSendGridのAPIキーが正しく設定されているか確認
- [ ] `SMTP_SERVER` が `smtp.sendgrid.net` になっているか確認
- [ ] `SMTP_PORT` が `587` または `465` になっているか確認
- [ ] SendGridのDomain Authenticationが「Verified」になっているか確認
- [ ] スパムフォルダを確認
- [ ] ログから認証コードを確認（メール送信に失敗した場合）

---

## 💡 ログの共有

エラーの詳細を確認するために、Railwayの「HTTP Logs」で以下の情報を確認してください：

1. **エラーメッセージの全文**
2. **`[2FA Email]` で始まるログ**
3. **`[2FA Setup]` で始まるログ**

これらの情報があれば、より具体的な解決方法を提案できます。

---

**まず、Railwayの「HTTP Logs」で `[2FA Email]` と検索して、エラーログを確認してください！**
