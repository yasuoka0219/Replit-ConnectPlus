# Gmail SMTP接続エラーの修正手順

## 🔴 現在の問題

`OSError: [Errno 101] Network is unreachable` エラーが発生しています。
これは、RailwayからGmailのSMTPサーバーに接続できないことを示しています。

## ✅ まず試すこと：ログから認証コードを使用

ログに表示されている認証コードを使用して、2段階認証を設定できます：

**認証コード: `791678`**

1. 2段階認証設定画面で認証コードを入力: `791678`
2. 「確認して有効にする」をクリック
3. 2段階認証が有効になります

---

## 🔧 Gmail SMTP接続問題の解決方法

### 方法1: ポート465（SSL）を試す

Gmail SMTPはポート587（TLS）とポート465（SSL）の両方をサポートしています。
ポート465を試してみてください。

#### Railwayで環境変数を更新：

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465  # 587から465に変更
SMTP_USERNAME=0219ko@gmail.com
SMTP_PASSWORD=gfviqnlxdjdilfac
SMTP_FROM_EMAIL=0219ko@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

**注意**: ポート465を使用する場合、コードの修正が必要です（SSL接続を使用）。

### 方法2: タイムアウトとリトライを追加

SMTP接続のタイムアウトを延長し、リトライロジックを追加します。

---

## 🛠️ コードの修正

ポート465（SSL）をサポートするようにコードを修正します。
