#!/usr/bin/env python3
"""
セッションをクリアするスクリプト
ブラウザのCookieを削除できない場合に使用
"""
from app import app
from flask import session

with app.app_context():
    with app.test_request_context():
        session.clear()
        print("✓ セッションをクリアしました")









