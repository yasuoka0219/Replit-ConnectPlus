# RailwayでConoHaメールアドレスのSMTP設定

## ✅ メールアドレス作成完了

メールアドレス `katsuhiro.okazaki@bizcraft-studio.com` が正常に作成されました。

次に、このメールアドレスをシステムのメール送信機能で使用するための設定を行います。

---

## 🚀 Railwayで環境変数を設定

### ステップ1: ConoHa WINGのSMTP設定情報を確認

ConoHa WINGのメールサーバー設定情報：

```
SMTPサーバー: smtp.wing.conoha.jp
または
SMTPサーバー: smtp.conoha.jp
SMTPポート: 587（推奨）または 465
SMTP認証: 必要
ユーザー名: katsuhiro.okazaki@bizcraft-studio.com
パスワード: メールボックス作成時に設定したパスワード
```

**注意:**
- 正確なSMTPサーバー名は、ConoHa WINGのメール設定画面で確認できます
- メールボックスの設定画面にSMTP情報が表示されている場合があります

### ステップ2: Railwayダッシュボードを開く

1. **Railwayにアクセス**
   - https://railway.app にアクセス
   - ログイン

2. **プロジェクトを選択**
   - 使用しているプロジェクトを選択

3. **「web」サービスを選択**
   - サービス一覧から「web」を選択

### ステップ3: 環境変数を設定

1. **「Variables」タブを開く**
   - 左サイドバーまたは上部のタブから「Variables」を選択

2. **環境変数を追加/更新**
   - 以下の環境変数を設定：

```bash
SMTP_SERVER=smtp.wing.conoha.jp
SMTP_PORT=587
SMTP_USERNAME=katsuhiro.okazaki@bizcraft-studio.com
SMTP_PASSWORD=your-mailbox-password
SMTP_FROM_EMAIL=katsuhiro.okazaki@bizcraft-studio.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**重要:**
- `SMTP_SERVER`: `smtp.wing.conoha.jp` または `smtp.conoha.jp`
  - 正確なサーバー名は、ConoHa WINGのメール設定画面で確認してください
- `SMTP_PORT`: `587`（推奨）または `465`
- `SMTP_USERNAME`: メールアドレス全体（`katsuhiro.okazaki@bizcraft-studio.com`）
- `SMTP_PASSWORD`: メールボックス作成時に設定したパスワード
- `SMTP_FROM_EMAIL`: 同じメールアドレス（`katsuhiro.okazaki@bizcraft-studio.com`）
- `SMTP_FROM_NAME`: `CONNECT+ CRM`（任意の名前）

3. **環境変数を保存**
   - 各環境変数を入力後、「Add」または「Save」をクリック
   - すべての環境変数が追加されるまで繰り返し

### ステップ4: 再デプロイ

1. **「Deployments」タブを開く**
   - 左サイドバーまたは上部のタブから「Deployments」を選択

2. **「Redeploy」をクリック**
   - 最新のデプロイを選択
   - 「Redeploy」ボタンをクリック
   - または、環境変数を保存すると自動的に再デプロイが開始される場合があります

3. **デプロイの完了を待つ**
   - 通常、数分かかります
   - デプロイが完了するまで待ちます

### ステップ5: 動作確認

1. **アプリケーションにアクセス**
   - RailwayのURLにアクセス
   - ログイン

2. **2段階認証を設定**
   - 「設定」→「2段階認証設定」
   - 「2段階認証を設定する（メール認証）」をクリック

3. **メールを確認**
   - `katsuhiro.okazaki@bizcraft-studio.com` に認証コードが届くことを確認
   - 認証コードを入力して2段階認証を有効化

✅ **完了！** ConoHaのメールアドレスからメールが正常に送信されるようになりました。

---

## 🔍 トラブルシューティング

### メールが届かない場合

1. **環境変数を確認**
   - Railwayダッシュボード → 「Variables」
   - 以下が正しく設定されているか確認：
     - `SMTP_SERVER`が正しいか（`smtp.wing.conoha.jp` または `smtp.conoha.jp`）
     - `SMTP_USERNAME`がメールアドレス全体になっているか
     - `SMTP_PASSWORD`が正しいか

2. **SMTPサーバー名を確認**
   - ConoHa WINGのメール設定画面で、正確なSMTPサーバー名を確認
   - 必要に応じて、`smtp.wing.conoha.jp` と `smtp.conoha.jp` の両方を試す

3. **ポートを変更してみる**
   - ポート587が失敗する場合、ポート465を試す：
     ```bash
     SMTP_PORT=465
     ```
   - コードは自動的にポート465（SSL）をサポートしています

4. **ログを確認**
   - Railwayダッシュボード → 「HTTP Logs」
   - `[2FA Email]`で始まるログを確認
   - エラーメッセージがないか確認

### よくあるエラー

#### `SMTPAuthenticationError`
- **原因**: メールアドレスまたはパスワードが正しくない
- **解決**: 
  - `SMTP_USERNAME`がメールアドレス全体（`katsuhiro.okazaki@bizcraft-studio.com`）になっているか確認
  - `SMTP_PASSWORD`が正しいか確認

#### `Network is unreachable`
- **原因**: SMTPサーバー名が正しくない、またはポートがブロックされている
- **解決**: 
  - `SMTP_SERVER`が正しいか確認（`smtp.wing.conoha.jp` または `smtp.conoha.jp`）
  - ポート465を試す

#### `Connection timeout`
- **原因**: ネットワークの問題、またはポートがブロックされている
- **解決**: 
  - ポート465を試す
  - ConoHaサポートに問い合わせ

---

## 📋 チェックリスト

- [x] メールアドレス作成完了（`katsuhiro.okazaki@bizcraft-studio.com`）
- [ ] ConoHa WINGでSMTP設定情報を確認
- [ ] Railwayで環境変数を設定
- [ ] 再デプロイ
- [ ] 2段階認証設定を試す
- [ ] メールが届くことを確認

---

## 💡 補足情報

### 送信元メールアドレスの変更

複数のメールアドレスを作成した場合、環境変数で`SMTP_FROM_EMAIL`を変更するだけで、送信元メールアドレスを変更できます。

例：
- 2段階認証: `katsuhiro.okazaki@bizcraft-studio.com`
- 顧客へのメール: `info@bizcraft-studio.com`（別のメールアドレスを作成した場合）

### メールアドレスの用途

現在作成されているメールアドレス `katsuhiro.okazaki@bizcraft-studio.com` は、以下の用途で使用できます：

- 2段階認証の認証コード送信
- パスワードリセットメール
- 顧客へのメール送信（連絡先へのメール送信機能）

---

**これで、ConoHaのメールアドレスからメールが送信されるようになります！**
