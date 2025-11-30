#!/usr/bin/env python3
"""
パスワードリセットメールの実際の内容を表示するスクリプト
"""
import os
from datetime import datetime, timedelta

# サンプルユーザー情報
sample_user_name = "岡崎雄大"
sample_user_email = "okazakikatsuhiro@icloud.com"
sample_token = "example_reset_token_1234567890abcdef"
sample_reset_url = f"http://localhost:5001/reset-password/{sample_token}"

print("=" * 80)
print("パスワードリセットメールの内容")
print("=" * 80)

print("\n【メールヘッダー】")
print("-" * 80)
print(f"件名: CONNECT+ CRM - パスワードリセット")
print(f"送信元: CONNECT+ CRM <{os.environ.get('SMTP_FROM_EMAIL', 'noreply@connectplus.local')}>")
print(f"宛先: {sample_user_email}")
print(f"送信日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")

print("\n" + "=" * 80)
print("【プレーンテキスト版（テキストメールクライアント用）】")
print("=" * 80)
print(f"""
CONNECT+ CRM - パスワードリセット

こんにちは、{sample_user_name}さん

パスワードをリセットするリクエストを受け付けました。

以下のリンクをクリックして、新しいパスワードを設定してください：

{sample_reset_url}

このリンクは24時間有効です。

このメールに心当たりがない場合は、無視してください。パスワードは変更されません。

---
このメールは CONNECT+ CRM から自動送信されています。
""")

print("\n" + "=" * 80)
print("【HTML版（ブラウザやHTML対応メールクライアントで表示される内容）】")
print("=" * 80)
print("""
メールクライアントで表示される内容:

┌─────────────────────────────────────────────────────────────┐
│  CONNECT+ CRM - パスワードリセット                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  こんにちは、{sample_user_name}さん                          │
│                                                              │
│  パスワードをリセットするリクエストを受け付けました。        │
│  以下のボタンをクリックして、新しいパスワードを設定してください。│
│                                                              │
│  ┌──────────────────────────────────────┐                  │
│  │   [パスワードをリセット] ボタン        │                  │
│  └──────────────────────────────────────┘                  │
│                                                              │
│  もしくは、以下のリンクをコピーしてブラウザのアドレスバーに  │
│  貼り付けてください：                                        │
│                                                              │
│  {sample_reset_url}                                         │
│                                                              │
│  ⚠️ このリンクは24時間有効です。                            │
│                                                              │
│  このメールに心当たりがない場合は、無視してください。        │
│  パスワードは変更されません。                                │
│                                                              │
│  ───────────────────────────────────────────────────────    │
│  このメールは CONNECT+ CRM から自動送信されています。        │
│  もしこのリクエストを送信していない場合は、                  │
│  アカウントのセキュリティをご確認ください。                  │
└─────────────────────────────────────────────────────────────┘
""".format(sample_user_name=sample_user_name, sample_reset_url=sample_reset_url))

print("\n" + "=" * 80)
print("【HTMLソースコード（実際に送信されるHTML）】")
print("=" * 80)
html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #4F46E5;">CONNECT+ CRM - パスワードリセット</h2>
      <p>こんにちは、{sample_user_name}さん</p>
      <p>パスワードをリセットするリクエストを受け付けました。</p>
      <p>以下のボタンをクリックして、新しいパスワードを設定してください。</p>
      
      <div style="text-align: center; margin: 30px 0;">
        <a href="{sample_reset_url}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
          パスワードをリセット
        </a>
      </div>
      
      <p style="color: #666; font-size: 14px;">
        もしくは、以下のリンクをコピーしてブラウザのアドレスバーに貼り付けてください：
      </p>
      <p style="background-color: #F3F4F6; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 12px; color: #666;">
        {sample_reset_url}
      </p>
      
      <p style="color: #666; font-size: 14px; margin-top: 20px;">
        <strong>このリンクは24時間有効です。</strong><br>
        このメールに心当たりがない場合は、無視してください。パスワードは変更されません。
      </p>
      
      <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
      <p style="color: #999; font-size: 12px;">
        このメールは CONNECT+ CRM から自動送信されています。<br>
        もしこのリクエストを送信していない場合は、アカウントのセキュリティをご確認ください。
      </p>
    </div>
  </body>
</html>
"""
print(html_content)

print("\n" + "=" * 80)
print("【メールの特徴】")
print("=" * 80)
print("""
✓ HTMLとプレーンテキストの両方を含む（マルチパートメール）
✓ 青い「パスワードをリセット」ボタンが表示される
✓ テキストリンクも併記されている
✓ 24時間の有効期限が明記されている
✓ セキュリティ警告が含まれている
✓ 日本語対応（UTF-8エンコーディング）
✓ レスポンシブデザイン（モバイルでも見やすい）
""")

print("\n" + "=" * 80)
print("【実際にメールを送信する場合】")
print("=" * 80)
print("""
1. ブラウザで http://localhost:5001/forgot-password にアクセス
2. メールアドレスを入力して「リセットリンクを送信」をクリック
3. SMTP設定がある場合: 実際のメールが送信されます
4. SMTP設定がない場合: サーバーのコンソールにリセットリンクが表示されます

開発モード（SMTP設定なし）の場合、コンソールに以下のように表示されます：
  [Password Reset Email] ⚠️ SMTP設定がありません。開発モードで動作しています。
  [Password Reset Email] パスワードリセットURL: http://localhost:5001/reset-password/xxxxx...
  [Password Reset Email] ユーザー: okazakikatsuhiro@icloud.com
""")

print("=" * 80)

