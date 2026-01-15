# Gmail SMTP設定ガイド - CONNECT+ CRM

Gmail SMTPを設定して、CONNECT+ CRMのメール送信機能を有効化する手順です。

## ✅ はい、Gmailで登録すれば使えます！

Gmail SMTPを設定すれば、CONNECT+ CRMで以下のメール送信機能が使えるようになります：

- ✅ **2段階認証コード送信**: ログイン時にメールで認証コードを送信
- ✅ **2FA設定時の認証コード送信**: 2段階認証を有効化する際の確認コード
- ✅ **パスワードリセットメール**: パスワード忘れ時のリセットリンク送信

---

## 🚀 設定手順（約5分）

### ステップ1: Gmailアカウントの準備

**必要なもの：**
- Gmailアカウント（既にある場合はそのまま使用）
- 2段階認証が有効になっていること

**確認方法：**
1. https://myaccount.google.com/security にアクセス
2. 「2段階認証プロセス」が「オン」になっているか確認
3. オフの場合は有効化

---

### ステップ2: アプリパスワードの生成（重要）

GmailのSMTPを使用するには、通常のパスワードではなく「アプリパスワード」が必要です。

1. **Googleアカウント設定にアクセス**
   - https://myaccount.google.com/security
   - または、Gmail → 右上のアカウントアイコン → 「Googleアカウントを管理」→「セキュリティ」

2. **アプリパスワードを選択**
   - 「2段階認証プロセス」の下にある「アプリパスワード」をクリック
   - 2段階認証が有効になっていない場合は、先に有効化が必要です

3. **アプリパスワードを生成**
   - 「アプリを選択」→「メール」を選択
   - 「デバイスを選択」→「その他（カスタム名）」を選択
   - 名前を入力：`CONNECT+ CRM`（任意の名前でOK）
   - 「生成」をクリック

4. **パスワードをコピー**
   - 16文字のパスワードが表示されます（例: `abcd efgh ijkl mnop`）
   - **重要**: このパスワードは一度しか表示されません！
   - 安全な場所に保存してください

---

### ステップ3: 環境変数の設定

本番環境の種類に応じて、以下のいずれかの方法で環境変数を設定します。

#### 方法A: Railwayの場合

1. Railwayダッシュボード → プロジェクト → 「Variables」
2. 以下の環境変数を追加：

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**重要**: 
- `SMTP_USERNAME`にはGmailアドレスを入力
- `SMTP_PASSWORD`には生成した16文字のアプリパスワードを入力（スペースは削除）
- `SMTP_FROM_EMAIL`には同じGmailアドレスを入力

3. 「Deployments」→「Redeploy」

#### 方法B: Renderの場合

1. Renderダッシュボード → サービス → 「Environment」
2. 上記の環境変数を追加
3. 「Manual Deploy」→「Deploy latest commit」

#### 方法C: Herokuの場合

```bash
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USERNAME=your-email@gmail.com
heroku config:set SMTP_PASSWORD=abcdefghijklmnop
heroku config:set SMTP_FROM_EMAIL=your-email@gmail.com
heroku config:set SMTP_FROM_NAME="CONNECT+ CRM"
heroku restart
```

#### 方法D: VPS（サーバー）の場合

```bash
# サーバーにSSH接続
ssh user@your-server-ip

# アプリケーションディレクトリに移動
cd /var/www/connectplus

# .envファイルを編集
nano .env
```

`.env`ファイルに以下を追加：

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

保存して終了（Ctrl+X → Y → Enter）

```bash
# アプリケーションを再起動
sudo systemctl restart connectplus
```

#### 方法E: ローカル開発環境の場合

```bash
# プロジェクトディレクトリに移動
cd /path/to/Replit-ConnectPlus-main

# .envファイルを編集
nano .env
# または
code .env
```

`.env`ファイルに以下を追加：

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

---

### ステップ4: 動作確認

1. **アプリケーションにアクセス**
   - 本番環境のURLにアクセス
   - ログイン

2. **2段階認証の設定**
   - 「設定」→「2段階認証設定」を開く
   - 「2段階認証を設定する（メール認証）」をクリック

3. **メールの確認**
   - Gmailを確認
   - 認証コードが記載されたメールが届いているか確認
   - 数秒〜1分程度で届きます

4. **認証コードの入力**
   - メールに記載されている6桁のコードを入力
   - 「確認して有効にする」をクリック

5. **成功の確認**
   - 「2段階認証が有効です」と表示されれば成功！

---

## 🎉 完了！

これで、CONNECT+ CRMのメール送信機能が有効になりました！

### 利用可能な機能

- ✅ **2段階認証コード送信**: ログイン時にメールで認証コードを送信
- ✅ **2FA設定時の認証コード送信**: 2段階認証を有効化する際の確認コード
- ✅ **パスワードリセットメール**: パスワード忘れ時のリセットリンク送信

---

## ⚠️ 重要な注意事項

### 1. アプリパスワードについて

- **通常のGmailパスワードは使えません**
- **アプリパスワードが必要です**
- アプリパスワードは16文字の文字列です（スペースは削除して使用）

### 2. 送信制限

- **1日500通まで**送信可能
- これを超えると、その日は送信できなくなります
- 小規模な運用であれば問題ありません

### 3. セキュリティ

- アプリパスワードは安全に保管してください
- 環境変数に設定する際は、スペースを削除してください
- アプリパスワードが漏洩した場合は、すぐに削除して再生成してください

---

## 🔍 トラブルシューティング

### メールが届かない場合

1. **アプリパスワードを確認**
   - 正しいアプリパスワードを設定しているか確認
   - スペースが含まれていないか確認（スペースは削除）

2. **2段階認証を確認**
   - 2段階認証が有効になっているか確認
   - アプリパスワードは2段階認証が有効でないと生成できません

3. **環境変数を確認**
   - `SMTP_USERNAME`にGmailアドレスが正しく設定されているか
   - `SMTP_PASSWORD`にアプリパスワードが正しく設定されているか
   - スペースが含まれていないか確認

4. **ログを確認**
   - 本番環境のログでエラーメッセージを確認
   - `[2FA Email] ❌`で始まるエラーメッセージがないか確認

### 認証エラーが発生する場合

**エラーメッセージ：**
```
[2FA Email] ❌ SMTP認証エラー: ...
```

**対処法：**

1. **アプリパスワードを再生成**
   - Googleアカウント設定 → セキュリティ → アプリパスワード
   - 古いパスワードを削除
   - 新しいパスワードを生成
   - 環境変数を更新

2. **2段階認証を確認**
   - 2段階認証が有効になっているか確認

3. **パスワードの形式を確認**
   - アプリパスワードは16文字の文字列です
   - スペースは削除してください

---

## 📊 Gmail SMTPの制限

| 項目 | 制限 |
|-----|------|
| **1日の送信数** | 500通まで |
| **1時間の送信数** | 制限あり |
| **1通あたりの受信者数** | 100人まで |
| **ファイル添付** | 25MBまで |

**注意**: これらの制限を超えると、メールが送信できなくなります。

---

## 💡 送信制限に達した場合

1日500通の制限に達した場合：

1. **翌日まで待つ**: 制限は1日ごとにリセットされます
2. **別のGmailアカウントを使用**: 複数のGmailアカウントで分散
3. **他のサービスに移行**: MailgunやAmazon SESを検討

---

## 📚 参考資料

- [本番環境メール機能実装手順](./PRODUCTION_EMAIL_SETUP.md)
- [SendGridが使えない場合の代替案](./ALTERNATIVE_EMAIL_SERVICES.md)
- [Gmailアプリパスワードの公式ガイド](https://support.google.com/accounts/answer/185833)

---

## まとめ

- ✅ **Gmail SMTPを設定すれば、CONNECT+ CRMでメール送信機能が使えます**
- ✅ **設定は約5分で完了**
- ✅ **完全無料で利用可能**
- ⚠️ **送信制限：1日500通まで**

小規模な運用であれば、Gmail SMTPで十分です！
