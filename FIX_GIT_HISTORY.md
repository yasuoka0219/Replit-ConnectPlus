# Git履歴からAPIキーを削除する方法

## 🔍 問題

過去のコミット（`7a5d1e886407dd67e7090ccca992ff4b50b63c47`）にAPIキーが含まれているため、GitHubのPush Protectionがプッシュをブロックしています。

## 🔧 解決策

過去のコミット履歴からAPIキーを削除する必要があります。

---

## 📋 手順

### 方法1: git filter-branchを使用（推奨）

以下のコマンドを実行してください：

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch SENDGRID_API_IMPLEMENTATION.md SENDGRID_API_SOLUTION.md SMTP_CONNECTION_FIX.md" \
  --prune-empty --tag-name-filter cat -- --all
```

その後、強制プッシュ：

```bash
git push origin --force --all
```

**注意**: 強制プッシュは履歴を書き換えるため、慎重に実行してください。

---

### 方法2: GitHubのURLで一時的に許可（簡単だが非推奨）

GitHubが提供しているURLにアクセスして、この特定のシークレットを一時的に許可することもできます：

```
https://github.com/yasuoka0219/Replit-ConnectPlus/security/secret-scanning/unblock-secret/38cUak8Y8zwspQ7XkSdLKLLlbYW
```

ただし、これはセキュリティ上推奨されません。

---

## ⚠️ 注意事項

- 強制プッシュは履歴を書き換えるため、他の開発者がいる場合は注意が必要です
- 過去のコミットを修正するため、コミットハッシュが変更されます
- バックアップを取ってから実行することを推奨します

---

**まず、方法1を試してください。問題が発生した場合は、方法2を検討してください。**
