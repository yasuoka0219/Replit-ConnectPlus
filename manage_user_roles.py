#!/usr/bin/env python3
"""
ユーザーのロールを管理するスクリプト

使用方法:
  # すべてのユーザーを表示
  python3 manage_user_roles.py list

  # ユーザーのロールを変更
  python3 manage_user_roles.py set <email> <role>

  # 例: demo@example.com をリーダーに変更
  python3 manage_user_roles.py set demo@example.com lead

利用可能なロール: admin, lead, member, viewer
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

# アプリケーションコンテキストが必要なため、app.pyからインポート
from database import db
from models import User

# Flaskアプリケーションのコンテキストで実行
from app import app

VALID_ROLES = ['admin', 'lead', 'member', 'viewer']

def list_users():
    """すべてのユーザーを表示"""
    print("\n" + "=" * 60)
    print("ユーザー一覧")
    print("=" * 60)
    print(f"{'ID':<5} {'名前':<20} {'メールアドレス':<30} {'ロール':<10}")
    print("-" * 60)
    
    users = User.query.order_by(User.created_at).all()
    for user in users:
        print(f"{user.id:<5} {user.name:<20} {user.email:<30} {user.role:<10}")
    
    print("=" * 60)
    print(f"合計: {len(users)}ユーザー")
    print()

def set_user_role(email, role):
    """ユーザーのロールを変更"""
    if role not in VALID_ROLES:
        print(f"エラー: 無効なロール '{role}'")
        print(f"利用可能なロール: {', '.join(VALID_ROLES)}")
        return False
    
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"エラー: ユーザー '{email}' が見つかりません")
        return False
    
    old_role = user.role
    user.role = role
    db.session.commit()
    
    print(f"✓ ユーザー '{user.name}' ({email}) のロールを変更しました")
    print(f"  変更前: {old_role}")
    print(f"  変更後: {role}")
    return True

def show_user(email):
    """特定のユーザー情報を表示"""
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"エラー: ユーザー '{email}' が見つかりません")
        return False
    
    print("\n" + "=" * 60)
    print("ユーザー情報")
    print("=" * 60)
    print(f"ID: {user.id}")
    print(f"名前: {user.name}")
    print(f"メールアドレス: {user.email}")
    print(f"ロール: {user.role}")
    print(f"登録日: {user.created_at.strftime('%Y年%m月%d日 %H:%M:%S')}")
    if user.team:
        print(f"チーム: {user.team.name}")
    print("=" * 60)
    print()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    with app.app_context():
        if command == 'list':
            list_users()
        elif command == 'set':
            if len(sys.argv) < 4:
                print("エラー: メールアドレスとロールを指定してください")
                print("使用方法: python3 manage_user_roles.py set <email> <role>")
                sys.exit(1)
            email = sys.argv[2]
            role = sys.argv[3].lower()
            set_user_role(email, role)
        elif command == 'show':
            if len(sys.argv) < 3:
                print("エラー: メールアドレスを指定してください")
                print("使用方法: python3 manage_user_roles.py show <email>")
                sys.exit(1)
            email = sys.argv[2]
            show_user(email)
        else:
            print(f"エラー: 不明なコマンド '{command}'")
            print(__doc__)
            sys.exit(1)

if __name__ == '__main__':
    main()

