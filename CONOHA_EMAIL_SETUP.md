# ConoHaメールアドレス取得と設定ガイド

## ✅ 概要

ConoHaで取得したドメインからメールアドレスを取得し、このシステムのメール送信機能で使用できます。

**2つの方法があります：**

1. **ConoHaのメールサーバーを直接使用**（推奨：簡単）
   - ConoHaでメールアドレスを作成
   - ConoHaのSMTPサーバーを使用
   - 追加費用なし（メールボックス料金のみ）

2. **SendGridのDomain Authenticationを使用**
   - ConoHaでメールアドレスを作成（任意）
   - SendGridでDomain Authenticationを設定
   - より高機能だが設定が複雑

---

## 🚀 方法1: ConoHaのメールサーバーを直接使用（推奨）

### ステップ1: ConoHaでメールアドレスを作成（約5分）

1. **ConoHaコントロールパネルにログイン**
   - https://www.conoha.jp/ にアクセス
   - コントロールパネルにログイン

2. **メールボックスを作成**
   - 「メール」→「メールボックス」を選択
   - 「メールボックス作成」をクリック

3. **メールアドレスを設定**
   - メールアドレス: `noreply@example.com`（例）
   - パスワード: 強力なパスワードを設定
   - 容量: 必要に応じて設定（例: 1GB）

4. **メールボックスを作成**
   - 「作成」をクリック
   - メールアドレスが作成されます

### ステップ2: ConoHaのSMTP設定情報を確認（約2分）

ConoHaのメールサーバー設定情報：

```
SMTPサーバー: smtp.conoha.jp
SMTPポート: 587（推奨）または 465
SMTP認証: 必要
ユーザー名: メールアドレス全体（例: noreply@example.com）
パスワード: メールボックス作成時に設定したパスワード
```

**注意:**
- ポート587: STARTTLS（推奨）
- ポート465: SSL/TLS
- ポート25: 通常は使用不可（セキュリティ上の理由）

### ステップ3: Railwayで環境変数を設定（1分）

1. **Railwayダッシュボードを開く**
   - https://railway.app にアクセス
   - プロジェクトを選択
   - 「web」サービスを選択

2. **環境変数を設定**
   - 「Variables」タブを開く
   - 以下の環境変数を設定：

```bash
SMTP_SERVER=smtp.conoha.jp
SMTP_PORT=587
SMTP_USERNAME=noreply@example.com
SMTP_PASSWORD=your-mailbox-password
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**重要:**
- `SMTP_USERNAME`はメールアドレス全体（例: `noreply@example.com`）
- `SMTP_PASSWORD`はメールボックス作成時に設定したパスワード
- `SMTP_FROM_EMAIL`は同じメールアドレス

3. **保存して再デプロイ**
   - 環境変数を保存
   - 「Deployments」タブ → 「Redeploy」をクリック

### ステップ4: 動作確認（1分）

1. **アプリケーションにアクセス**
   - RailwayのURLにアクセス
   - ログイン

2. **2段階認証を設定**
   - 「設定」→「2段階認証設定」
   - 「2段階認証を設定する（メール認証）」をクリック

3. **メールを確認**
   - 設定したメールアドレス（例: `noreply@example.com`）から認証コードが届くことを確認
   - 認証コードを入力して2段階認証を有効化

✅ **完了！** ConoHaのメールアドレスからメールが正常に送信されるようになりました。

---

## 🔄 方法2: SendGridのDomain Authenticationを使用

ConoHaでメールアドレスを取得した後、SendGridのDomain Authenticationを使用することもできます。

### ステップ1: ConoHaでメールアドレスを作成（任意）

- 上記の「方法1」のステップ1を参照
- メールアドレスは任意（SendGridで使用する場合は必須ではありません）

### ステップ2: SendGridでDomain Authenticationを設定

- 詳細は `CUSTOM_DOMAIN_SETUP.md` を参照
- ConoHaで取得したドメインをSendGridで認証

### ステップ3: Railwayで環境変数を設定

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=CONNECT+ CRM
```

---

## 🔍 トラブルシューティング

### メールが届かない場合

1. **環境変数を確認**
   - Railwayダッシュボード → 「Variables」
   - 以下が正しく設定されているか確認：
     - `SMTP_SERVER=smtp.conoha.jp`
     - `SMTP_PORT=587`
     - `SMTP_USERNAME`がメールアドレス全体になっているか
     - `SMTP_PASSWORD`が正しいか

2. **ConoHaのメールサーバー設定を確認**
   - ConoHaコントロールパネル → 「メール」→「メールボックス」
   - メールアドレスが正しく作成されているか確認

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
  - `SMTP_USERNAME`がメールアドレス全体（例: `noreply@example.com`）になっているか確認
  - `SMTP_PASSWORD`が正しいか確認

#### `Network is unreachable`
- **原因**: ポートがブロックされている、またはSMTPサーバーが正しくない
- **解決**: 
  - `SMTP_SERVER=smtp.conoha.jp`が正しいか確認
  - ポート465を試す

#### `Connection timeout`
- **原因**: ネットワークの問題、またはポートがブロックされている
- **解決**: 
  - ポート465を試す
  - ConoHaのサポートに問い合わせ

---

## 📋 チェックリスト（方法1: ConoHa直接使用）

- [ ] ConoHaコントロールパネルにログイン
- [ ] メールボックスを作成
- [ ] メールアドレスとパスワードを確認
- [ ] Railwayで環境変数を設定
- [ ] 再デプロイ
- [ ] 2段階認証設定を試す
- [ ] メールが届くことを確認

---

## 💡 補足情報

### ConoHaメールの料金

- **メールボックス料金**: 月額料金がかかります（プランによる）
- **送信制限**: プランによって1日の送信数に制限がある場合があります
- **詳細**: ConoHaの料金ページを確認してください

### メールアドレスの選択

会社用のメールアドレスとして、以下のようなものが一般的です：

- `noreply@example.com` - 返信不要の場合
- `info@example.com` - 一般的な問い合わせ
- `support@example.com` - サポート用
- `crm@example.com` - CRM専用
- `system@example.com` - システム用

### 複数のメールアドレスを使用する場合

ConoHaで複数のメールアドレスを作成し、用途に応じて使い分けることができます：

- 2段階認証: `noreply@example.com`
- パスワードリセット: `noreply@example.com`
- 顧客へのメール: `info@example.com`

環境変数で`SMTP_FROM_EMAIL`を変更するだけで、送信元メールアドレスを変更できます。

---

## 🆚 方法1と方法2の比較

| 項目 | 方法1: ConoHa直接 | 方法2: SendGrid |
|------|------------------|-----------------|
| **設定の簡単さ** | ⭐⭐⭐⭐⭐ 簡単 | ⭐⭐⭐ やや複雑 |
| **追加費用** | メールボックス料金のみ | SendGrid無料プラン |
| **送信制限** | ConoHaのプランによる | 1日100通（無料プラン） |
| **機能** | 基本的なメール送信 | 高機能（分析、テンプレートなど） |
| **推奨** | ✅ 小規模な運用 | 大規模な運用 |

**小規模なCRM運用の場合、方法1（ConoHa直接使用）がおすすめです。**

---

**これで、ConoHaで取得したドメインからメールが送信されるようになります！**
