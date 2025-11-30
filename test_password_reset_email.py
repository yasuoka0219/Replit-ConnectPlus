#!/usr/bin/env python3
"""
パスワードリセットメールの内容を確認するテストスクリプト

使用方法:
  python3 test_password_reset_email.py <email>

  # 例: okazakikatsuhiro@icloud.com のパスワードリセットメールを確認
  python3 test_password_reset_email.py okazakikatsuhiro@icloud.com

このスクリプトは:
  1. ユーザーを検索
  2. リセットトークンを生成
  3. メールの内容をコンソールに表示（実際には送信しません）
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

from database import db
from models import User, PasswordResetToken
from utils.password_reset import generate_reset_token, send_password_reset_email, RESET_TOKEN_EXPIRY_HOURS
from datetime import datetime, timedelta
from flask import Flask, url_for

from app import app

def test_password_reset_email(email):
    """パスワードリセットメールの内容を確認"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"エラー: ユーザー '{email}' が見つかりません")
            return False
        
        print("=" * 60)
        print("パスワードリセットメール確認")
        print("=" * 60)
        print(f"\nユーザー情報:")
        print(f"  名前: {user.name}")
        print(f"  メールアドレス: {user.email}")
        print(f"  ロール: {user.role}")
        
        # トークンを生成
        token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRY_HOURS)
        
        # リセットURLを生成
        with app.test_request_context():
            reset_url = url_for('reset_password', token=token, _external=True)
        
        print(f"\n生成されたトークン: {token}")
        print(f"有効期限: {expires_at.strftime('%Y年%m月%d日 %H:%M:%S')} (24時間後)")
        print(f"\nリセットURL:")
        print(f"  {reset_url}")
        
        print("\n" + "=" * 60)
        print("メールの内容（プレーンテキスト版）:")
        print("=" * 60)
        print(f"""
件名: CONNECT+ CRM - パスワードリセット

CONNECT+ CRM - パスワードリセット

こんにちは、{user.name}さん

パスワードをリセットするリクエストを受け付けました。

以下のリンクをクリックして、新しいパスワードを設定してください：

{reset_url}

このリンクは24時間有効です。

このメールに心当たりがない場合は、無視してください。パスワードは変更されません。

---
このメールは CONNECT+ CRM から自動送信されています。
        """)
        
        print("\n" + "=" * 60)
        print("メールの内容（HTML版 - ブラウザで表示される内容）:")
        print("=" * 60)
        print(f"""
件名: CONNECT+ CRM - パスワードリセット
送信元: CONNECT+ CRM <{os.environ.get('SMTP_FROM_EMAIL', 'noreply@connectplus.local')}>
宛先: {user.email}

---
CONNECT+ CRM - パスワードリセット

こんにちは、{user.name}さん

パスワードをリセットするリクエストを受け付けました。

以下のボタンをクリックして、新しいパスワードを設定してください：

[パスワードをリセット] ボタン
   → {reset_url}

もしくは、以下のリンクをコピーしてブラウザのアドレスバーに貼り付けてください：
{reset_url}

このリンクは24時間有効です。

このメールに心当たりがない場合は、無視してください。パスワードは変更されません。

---
このメールは CONNECT+ CRM から自動送信されています。
もしこのリクエストを送信していない場合は、アカウントのセキュリティをご確認ください。
        """)
        
        print("\n" + "=" * 60)
        print("実際にメールを送信する場合:")
        print("=" * 60)
        print("実際にメールを送信するには、以下のコマンドを実行してください:")
        print(f"  python3 -c \"from app import app; from database import db; from models import User, PasswordResetToken; from utils.password_reset import generate_reset_token, send_password_reset_email; from flask import url_for; from datetime import datetime, timedelta; import os; load_dotenv(); exec(open('send_test_reset_email.py').read())\"")
        
        print("\nまたは、ブラウザで以下にアクセスしてパスワードリセットをリクエストしてください:")
        print("  http://localhost:5001/forgot-password")
        print("\n" + "=" * 60)
        
        return True

def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 test_password_reset_email.py <email>")
        print("\n例:")
        print("  python3 test_password_reset_email.py okazakikatsuhiro@icloud.com")
        sys.exit(1)
    
    email = sys.argv[1]
    test_password_reset_email(email)

if __name__ == '__main__':
    main()

