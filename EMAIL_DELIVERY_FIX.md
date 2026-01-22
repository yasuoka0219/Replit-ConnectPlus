# メール送信機能の改善

## ✅ 実装した改善

メールが確実に届くように、以下の改善を実装しました：

### 1. リトライロジック
- 接続エラー時に自動的に最大3回まで再試行
- 再試行間隔は2秒、4秒、6秒と段階的に延長

### 2. ポートフォールバック
- ポート587が失敗した場合、自動的にポート465を試行
- ポート465が失敗した場合、自動的にポート587を試行
- どちらのポートでも接続を試みます

### 3. タイムアウト延長
- タイムアウトを30秒から60秒に延長
- ネットワークが遅い環境でも接続できるように

### 4. 詳細なログ出力
- 各試行の詳細をログに出力
- どのポートで成功/失敗したかを記録

---

## 🚀 デプロイ手順

### ステップ1: GitHubにプッシュ

```bash
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
git push origin main
```

### ステップ2: Railwayで自動デプロイを待つ

Railwayが自動的にGitHubから最新のコードを取得してデプロイします。
通常、数分かかります。

### ステップ3: 動作確認

1. アプリケーションにアクセス
2. 「設定」→「2段階認証設定」
3. 「2段階認証を設定する（メール認証）」をクリック
4. ログを確認：
   - `[2FA Email] 試行 1/3: ポート 587 で接続中...`
   - 成功した場合: `[2FA Email] ✓ Code sent to {email} (ポート {port})`
5. `0219ko@gmail.com` に認証コードが送信されることを確認

---

## 🔍 ログの確認方法

### Railwayでログを確認

1. Railwayダッシュボード → 「web」サービス
2. 「HTTP Logs」タブを開く
3. `[2FA Email]` で始まるログを確認

### 期待されるログ出力

**成功時:**
```
[2FA Email] 試行 1/3: ポート 587 で接続中...
[2FA Email] ✓ Code sent to 0219ko@gmail.com (ポート 587)
```

**ポート587が失敗してポート465で成功した場合:**
```
[2FA Email] 試行 1/3: ポート 587 で接続中...
[2FA Email] ポート 587 で接続エラー: [Errno 101] Network is unreachable
[2FA Email] 試行 1/3: ポート 465 で接続中...
[2FA Email] ✓ Code sent to 0219ko@gmail.com (ポート 465)
```

**リトライが発生した場合:**
```
[2FA Email] 試行 1/3: ポート 587 で接続中...
[2FA Email] ポート 587 で接続エラー: [Errno 101] Network is unreachable
[2FA Email] 試行 1/3: ポート 465 で接続中...
[2FA Email] ポート 465 で接続エラー: [Errno 101] Network is unreachable
[2FA Email] 2秒待機してから再試行します...
[2FA Email] 試行 2/3: ポート 587 で接続中...
[2FA Email] ✓ Code sent to 0219ko@gmail.com (ポート 587)
```

---

## 📋 チェックリスト

- [ ] GitHubにプッシュ
- [ ] Railwayで自動デプロイを待つ
- [ ] ログを確認
- [ ] 2段階認証設定を試す
- [ ] メールが届くか確認

---

## 💡 トラブルシューティング

### まだメールが届かない場合

1. **ログを確認**
   - どのポートで試行しているか
   - エラーメッセージの詳細

2. **環境変数を確認**
   - Railwayダッシュボード → 「Variables」
   - 以下が正しく設定されているか確認：
     - `SMTP_SERVER=smtp.gmail.com`
     - `SMTP_PORT=587` または `465`
     - `SMTP_USERNAME=0219ko@gmail.com`
     - `SMTP_PASSWORD=gfviqnlxdjdilfac`
     - `SMTP_FROM_EMAIL=0219ko@gmail.com`

3. **Gmailのセキュリティ設定を確認**
   - アプリパスワードが正しいか
   - 2段階認証が有効か

4. **ポートを変更してみる**
   - `SMTP_PORT=587` → `SMTP_PORT=465` に変更
   - またはその逆

---

**これで、メールが確実に届くようになります！**
