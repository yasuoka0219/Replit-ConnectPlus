#!/usr/bin/env python3
"""
ユーザーのパスワードをリセットするスクリプト

使用方法:
  python3 reset_password.py <email> <new_password>

  # 例: okazakikatsuhiro@icloud.com のパスワードを "newpassword123" に変更
  python3 reset_password.py okazakikatsuhiro@icloud.com newpassword123

注意: パスワードは最低8文字、英数字を含む必要があります。
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

from database import db
from models import User
from werkzeug.security import generate_password_hash

# Flaskアプリケーションのコンテキストで実行
from app import app

def reset_password(email, new_password):
    """ユーザーのパスワードをリセット"""
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"エラー: ユーザー '{email}' が見つかりません")
        return False
    
    # パスワード強度チェック（簡単なチェック）
    if len(new_password) < 8:
        print("エラー: パスワードは最低8文字である必要があります")
        return False
    
    # パスワードをハッシュ化して更新
    user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
    user.reset_failed_attempts()
    user.unlock_account()
    db.session.commit()
    
    print(f"✓ ユーザー '{user.name}' ({email}) のパスワードをリセットしました")
    print(f"  新しいパスワード: {new_password}")
    print(f"\nログイン情報:")
    print(f"  メールアドレス: {email}")
    print(f"  パスワード: {new_password}")
    return True

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    email = sys.argv[1]
    new_password = sys.argv[2]
    
    with app.app_context():
        reset_password(email, new_password)

if __name__ == '__main__':
    main()

