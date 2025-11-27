# 2段階認証（開発モード）ガイド

## 認証コードの確認方法

開発環境でSMTP設定がない場合、認証コードは**サーバーのコンソール（ターミナル）**に表示されます。

### 方法1: ログファイルを確認

認証コードは以下のログファイルに出力されます：

```bash
# 最新の30行を確認（認証コードを探す）
tail -30 /tmp/connectplus.log | grep -i "2fa\|code\|認証"

# または、すべてのログを確認
tail -f /tmp/connectplus.log
```

ログには以下のようなメッセージが表示されます：

```
[2FA Email] ⚠️ SMTP設定がありません。開発モードで動作しています。
[2FA Email] 認証コード: 123456
[2FA Email] メールアドレス: your-email@example.com
[2FA Email] .envファイルにSMTP設定を追加してください。
```

### 方法2: ターミナルで直接確認

サーバーをフォアグラウンドで実行している場合、ターミナルに直接表示されます：

```bash
# サーバーをフォアグラウンドで起動
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
python3 app.py
```

### 方法3: ログをリアルタイムで確認

新しいターミナルを開いて、以下のコマンドを実行：

```bash
# ログをリアルタイムで監視（Ctrl+Cで停止）
tail -f /tmp/connectplus.log
```

認証コードが生成されると、リアルタイムで表示されます。

## 認証コードの使用手順

1. **2段階認証を設定する**（設定ページで「2段階認証を設定する」ボタンをクリック）
2. **ログファイルまたはターミナルを確認**
   - ログファイル: `/tmp/connectplus.log`
   - または、サーバーを実行しているターミナル
3. **6桁の認証コードを見つける**
   - `[2FA Email] 認証コード: XXXXXX` という形式で表示されます
4. **そのコードを入力**
   - 設定画面の「認証コード（6桁）」フィールドに入力
   - 「確認して有効にする」ボタンをクリック

## 本番環境での使用

本番環境では、`.env`ファイルにSMTP設定を追加してください：

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

設定を追加すると、メールで認証コードが送信されます。

詳細は `EMAIL_2FA_SETUP.md` を参照してください。



