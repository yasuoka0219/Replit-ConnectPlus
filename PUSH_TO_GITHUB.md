# GitHubへのプッシュ手順

## 📋 必要な情報

### リポジトリ情報
- **URL**: https://github.com/yasuoka0219/Replit-ConnectPlus
- **ブランチ**: `main`
- **アカウント**: `yasuoka0219`

### 認証情報（いずれか1つ）

#### 方法1: Personal Access Token（PAT）
- GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- 必要なスコープ: `repo`（すべてのリポジトリへのアクセス権限）
- トークンをコピーして保存

#### 方法2: GitHub CLI（最も簡単・推奨）
- インストール: `brew install gh`
- ログイン: `gh auth login`

#### 方法3: SSH キー
- SSHキーを生成してGitHubに登録

## 🚀 実行手順

### ステップ1: 変更をコミット

```bash
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main

# すべての変更をステージング
git add .

# コミット（メッセージは自由に変更してください）
git commit -m "Add Google Calendar integration, email 2FA, and documentation updates"
```

### ステップ2: 認証方法を選択して設定

#### 方法A: Personal Access Token を使用

```bash
# リモートURLを更新（YOUR_TOKENを実際のトークンに置き換え）
git remote set-url origin https://yasuoka0219:YOUR_TOKEN@github.com/yasuoka0219/Replit-ConnectPlus.git
```

#### 方法B: GitHub CLI を使用（推奨）

```bash
# GitHub CLIをインストール（未インストールの場合）
brew install gh

# ログイン（ブラウザで認証）
gh auth login
```

#### 方法C: SSH を使用

```bash
# SSHキーを生成（既にある場合はスキップ）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 公開鍵を表示してGitHubに追加
cat ~/.ssh/id_ed25519.pub
# ↑ これを GitHub → Settings → SSH and GPG keys → New SSH key に追加

# リモートURLをSSHに変更
git remote set-url origin git@github.com:yasuoka0219/Replit-ConnectPlus.git
```

### ステップ3: プッシュ

```bash
# 通常のプッシュ
git push origin main

# または、リモートに既存のコミットがある場合
git push origin main --force-with-lease
```

## ⚡ 最速コマンド（GitHub CLI使用の場合）

```bash
cd /Users/okazakikatsuhiro/Downloads/Replit-ConnectPlus-main
git add .
git commit -m "Update project files"
gh auth login  # 初回のみ
git push origin main
```

## ⚠️ トラブルシューティング

### 403エラーが発生する場合

1. **トークンの権限を確認**
   - `repo` スコープが必要です
   - トークンが期限切れでないか確認

2. **GitHub CLIを使用する（推奨）**
   - 最も簡単で安全な方法です

3. **SSHキーを使用する**
   - 一度設定すれば、次回以降は認証不要です

### "Updates were rejected" エラー

リモートに既存のコミットがある場合：

```bash
# リモートの変更を確認
git fetch origin

# マージまたはリベース
git pull origin main --rebase
git push origin main
```

## 📝 現在の状態

- ✅ リモートURL設定済み: `https://github.com/yasuoka0219/Replit-ConnectPlus`
- ⚠️ 未コミットの変更あり（約26ファイル）
- ⚠️ 認証が必要

## 📚 参考

詳細な説明は `GITHUB_PUSH_COMPLETE.md` を参照してください。

