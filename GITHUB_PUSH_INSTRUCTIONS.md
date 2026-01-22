# GitHubへのプッシュ手順

## 🔐 認証が必要です

GitHubへのプッシュには認証が必要です。以下のいずれかの方法でプッシュしてください。

---

## 方法1: ターミナルから手動でプッシュ（推奨）

### ステップ1: ターミナルを開く

ターミナルアプリケーションを開いてください。

### ステップ2: プロジェクトディレクトリに移動

```bash
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
```

### ステップ3: GitHubにプッシュ

```bash
git push origin main
```

### ステップ4: 認証情報を入力

- **Username**: GitHubのユーザー名を入力
- **Password**: GitHubのPersonal Access Tokenを入力（通常のパスワードではありません）

**Personal Access Tokenの作成方法：**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 「Generate new token (classic)」をクリック
3. スコープで「repo」にチェック
4. 「Generate token」をクリック
5. 表示されたトークンをコピー（一度しか表示されません）

---

## 方法2: GitHub Desktopを使用

1. GitHub Desktopアプリを開く
2. リポジトリを開く
3. 「Push origin」ボタンをクリック

---

## 方法3: VS Codeからプッシュ

1. VS Codeでプロジェクトを開く
2. ソース管理パネルを開く
3. 「...」メニュー → 「Push」を選択

---

## 📋 プッシュする内容

以下の変更がプッシュされます：

1. **メール送信機能の追加**
   - 2段階認証メール送信
   - 連絡先へのメール送信機能
   - 汎用メール送信ユーティリティ

2. **2段階認証設定画面の表示修正**
   - 設定ページで2段階認証のリンクを常に表示

3. **各種ドキュメント**
   - メール送信機能の実装ガイド
   - SMTP設定ガイド
   - デプロイ手順

---

## ✅ プッシュ後の確認

プッシュが成功したら：

1. **GitHubで確認**
   - https://github.com/yasuoka0219/Replit-ConnectPlus にアクセス
   - 最新のコミットが表示されているか確認

2. **Railwayで自動デプロイを確認**
   - Railwayダッシュボードで新しいデプロイが開始されるか確認
   - デプロイが完了するまで数分待つ

3. **本番環境の環境変数を設定**
   - Railwayダッシュボード → 「Variables」
   - SMTP設定を追加：
     ```bash
     SMTP_SERVER=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USERNAME=0219ko@gmail.com
     SMTP_PASSWORD=gfviqnlxdjdilfac
     SMTP_FROM_EMAIL=0219ko@gmail.com
     SMTP_FROM_NAME=CONNECT+ CRM
     ```

4. **アプリケーションを再起動**
   - 「Deployments」→「Redeploy」

---

## 🆘 トラブルシューティング

### 認証エラーが発生する場合

1. **Personal Access Tokenを使用**
   - 通常のパスワードではなく、Personal Access Tokenを使用

2. **SSHキーを設定**
   - SSHキーを設定してSSH経由でプッシュ

3. **GitHub CLIを使用**
   ```bash
   gh auth login
   git push origin main
   ```

---

**プッシュが完了したら、Railwayで環境変数を設定して再デプロイしてください！**
