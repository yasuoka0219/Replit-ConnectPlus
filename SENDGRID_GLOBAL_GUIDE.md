# 海外版（グローバル）SendGridの利用ガイド

## ✅ 日本版と海外版の違い

| 項目 | 日本版（sendgrid.kke.co.jp） | 海外版（sendgrid.com） |
|------|------------------------------|-------------------------|
| **法人登録** | 必要 | 不要 |
| **個人・個人事業主** | 利用不可 | 利用可能 |
| **独自ドメイン** | 必要（法人向け） | 利用可能 |
| **フリーアドレス** | 利用不可 | Single Senderで利用可能 |
| **無料プラン** | あり | あり（1日100通） |
| **日本語** | あり | ダッシュボードは英語 |

---

## 🚀 海外版SendGridの登録手順

### ステップ1: アカウント作成（約5分）

1. **海外版SendGridにアクセス**
   - https://sendgrid.com にアクセス
   - **日本版（sendgrid.kke.co.jp）ではなく、こちらを使用**

2. **「Sign Up」をクリック**
   - トップページ右上の「Sign Up」をクリック

3. **アカウント情報を入力**
   - **Email**: メールアドレス（Gmail、会社メールどちらでもOK）
   - **Password**: 8文字以上
   - **Company Name**: 任意（個人の場合は姓名などでも可）

4. **利用規約に同意**
   - 「I'm not a robot」にチェック
   - 「I agree to the Terms of Service and Privacy Policy」にチェック

5. **「Create Account」をクリック**

6. **メール確認**
   - 登録したメールアドレスに確認メールが届く
   - リンクをクリックしてメールアドレスを認証

---

## 📧 送信元の2つの選び方

### 方法A: 独自ドメイン（Domain Authentication）【推奨】

- ドメイン: `bizcraft-studio.com` を使用
- 送信元例: `noreply@bizcraft-studio.com`
- 手順: 以前の `SENDGRID_REGISTRATION_GUIDE.md` の「Domain Authentication」の流れのまま
- ConoHaのDNSにCNAMEを追加して認証

### 方法B: フリーアドレス（Single Sender Verification）

- GmailやYahooなど既存のメールアドレスを「送信元」として登録
- そのアドレスに届く確認メールのリンクをクリックして認証
- 独自ドメインのDNS設定は不要

---

## 🔐 独自ドメインを使う場合（方法A）

1. ログイン: https://app.sendgrid.com  
2. **Settings** → **Sender Authentication**  
3. **Authenticate Your Domain** をクリック  
4. Domain: `bizcraft-studio.com` を入力 → **Next**  
5. 表示されたCNAMEレコードを、ConoHaのDNS設定に追加  
6. 反映後（数分〜数時間）、SendGridで **Verify** を実行  
7. **Verified** になれば、`noreply@bizcraft-studio.com` などで送信可能  

---

## 📬 フリーアドレスを使う場合（方法B）

1. ログイン: https://app.sendgrid.com  
2. **Settings** → **Sender Authentication**  
3. **Single Sender Verification** → **Create a Sender**  
4. 入力例:
   - From Name: `CONNECT+ CRM`
   - From Email: `katsuhiro.okazaki@bizcraft-studio.com` または Gmail など
   - Reply To: 同じアドレス
   - 住所・会社名など（必須欄のみ）  
5. **Create** 後、そのアドレスに届く確認メールのリンクをクリック  
6. 認証が完了すれば、そのアドレスを送信元に使える  

---

## 🔑 APIキー作成（共通）

1. **Settings** → **API Keys**  
2. **Create API Key**  
3. Name: `CONNECT+ CRM`、Permission: **Full Access**  
4. **Create & View** で表示されるAPIキーをコピー（この画面以外では表示されません）

---

## 🚂 Railwayの環境変数（SendGrid共通）

```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxx...（作成したAPIキー）
SMTP_FROM_EMAIL=noreply@bizcraft-studio.com
SMTP_FROM_NAME=CONNECT+ CRM
```

- 方法A（独自ドメイン）: `SMTP_FROM_EMAIL=noreply@bizcraft-studio.com` など  
- 方法B（Single Sender）: 認証したアドレス（Gmailなど）を `SMTP_FROM_EMAIL` に指定  

---

## 💡 おすすめ

- **`bizcraft-studio.com` を持っている**  
  → **方法A（Domain Authentication）** がおすすめ。  
  会社ドメインで統一でき、到達率や信頼性も高めです。

- **まず手軽に試したい**  
  → **方法B（Single Sender）** で、  
  `katsuhiro.okazaki@bizcraft-studio.com` や Gmail を認証して送信テストするのもありです。

---

## 📋 チェックリスト（海外版SendGrid）

- [ ] https://sendgrid.com でアカウント作成（法人登録不要）
- [ ] メール認証を完了
- [ ] 方法A: Domain Authentication で `bizcraft-studio.com` を認証  
  または 方法B: Single Sender で送信元アドレスを認証
- [ ] APIキーを作成
- [ ] Railway に上記の環境変数を設定
- [ ] 再デプロイして、2段階認証などで送信テスト

---

海外版SendGridであれば、法人登録なしで送信まで進められます。
