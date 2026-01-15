"""
Password reset utility
Generates reset tokens and sends password reset emails
"""
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from flask import current_app, url_for
from database import db


# Password reset configuration constants
RESET_TOKEN_LENGTH = 32
RESET_TOKEN_EXPIRY_HOURS = 24


def generate_reset_token(length=RESET_TOKEN_LENGTH):
    """
    Generate secure random token for password reset
    
    Args:
        length (int): Length of the token (default: 32)
        
    Returns:
        str: Secure random token
    """
    return secrets.token_urlsafe(length)


def send_password_reset_email(user, reset_token, reset_url):
    """
    Send password reset email with reset link
    
    Args:
        user (User): User object
        reset_token (str): Reset token
        reset_url (str): Full URL for password reset
        
    Returns:
        bool: True if email sent successfully
    """
    try:
        # Get email configuration from environment
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        smtp_from_email = os.environ.get('SMTP_FROM_EMAIL', smtp_username)
        smtp_from_name = os.environ.get('SMTP_FROM_NAME', 'CONNECT+ CRM')
        
        # If no SMTP credentials configured, use a mock/test mode
        if not smtp_username or not smtp_password:
            print(f"[Password Reset Email] ⚠️ SMTP設定がありません。開発モードで動作しています。")
            print(f"[Password Reset Email] パスワードリセットURL: {reset_url}")
            print(f"[Password Reset Email] ユーザー: {user.email}")
            print(f"[Password Reset Email] .envファイルにSMTP設定を追加してください。")
            return True  # Return True in development/test mode
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'CONNECT+ CRM - パスワードリセット'
        msg['From'] = f'{smtp_from_name} <{smtp_from_email}>'
        msg['To'] = user.email
        
        # Create HTML email body
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #4F46E5;">CONNECT+ CRM - パスワードリセット</h2>
              <p>こんにちは、{user.name}さん</p>
              <p>パスワードをリセットするリクエストを受け付けました。</p>
              <p>以下のボタンをクリックして、新しいパスワードを設定してください。</p>
              
              <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                  パスワードをリセット
                </a>
              </div>
              
              <p style="color: #666; font-size: 14px;">
                もしくは、以下のリンクをコピーしてブラウザのアドレスバーに貼り付けてください：
              </p>
              <p style="background-color: #F3F4F6; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 12px; color: #666;">
                {reset_url}
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
        
        # Plain text version
        text_body = f"""
CONNECT+ CRM - パスワードリセット

こんにちは、{user.name}さん

パスワードをリセットするリクエストを受け付けました。

以下のリンクをクリックして、新しいパスワードを設定してください：

{reset_url}

このリンクは24時間有効です。

このメールに心当たりがない場合は、無視してください。パスワードは変更されません。

---
このメールは CONNECT+ CRM から自動送信されています。
        """
        
        # Attach both versions
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email with retry and fallback logic
        import time
        import ssl
        import socket
        
        # Try both ports if one fails (587 first, then 465)
        ports_to_try = [smtp_port]
        if smtp_port == 587:
            ports_to_try.append(465)
        elif smtp_port == 465:
            ports_to_try.append(587)
        
        last_error = None
        max_retries = 3
        
        for attempt in range(max_retries):
            for port in ports_to_try:
                try:
                    print(f"[Password Reset Email] 試行 {attempt + 1}/{max_retries}: ポート {port} で接続中...")
                    
                    # Port 465 uses SSL, port 587 uses STARTTLS
                    if port == 465:
                        # Use SMTP_SSL for port 465
                        context = ssl.create_default_context()
                        with smtplib.SMTP_SSL(smtp_server, port, timeout=60, context=context) as server:
                            server.login(smtp_username, smtp_password)
                            server.send_message(msg)
                    else:
                        # Use SMTP with STARTTLS for port 587
                        with smtplib.SMTP(smtp_server, port, timeout=60) as server:
                            server.starttls()
                            server.login(smtp_username, smtp_password)
                            server.send_message(msg)
                    
                    print(f"[Password Reset Email] Reset link sent to {user.email} (ポート {port})")
                    return True
                    
                except (socket.error, OSError) as e:
                    # Network errors - try next port or retry
                    last_error = e
                    error_msg = f"[Password Reset Email] ポート {port} で接続エラー: {e}"
                    print(error_msg)
                    if port == ports_to_try[-1] and attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"[Password Reset Email] {wait_time}秒待機してから再試行します...")
                        time.sleep(wait_time)
                    continue
                    
                except smtplib.SMTPAuthenticationError as e:
                    # Authentication error - don't retry
                    raise
                    
                except smtplib.SMTPException as e:
                    # SMTP error - try next port or retry
                    last_error = e
                    error_msg = f"[Password Reset Email] ポート {port} でSMTPエラー: {e}"
                    print(error_msg)
                    if port == ports_to_try[-1] and attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"[Password Reset Email] {wait_time}秒待機してから再試行します...")
                        time.sleep(wait_time)
                    continue
        
        # All attempts failed
        raise Exception(f"すべての試行が失敗しました。最後のエラー: {last_error}")
        
        print(f"[Password Reset Email] Reset link sent to {user.email}")
        return True
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[Password Reset Email] ❌ メール送信エラー: {e}")
        print(f"[Password Reset Email] エラー詳細:\n{error_details}")
        
        # In development, still return True if credentials not configured
        if not smtp_username or not smtp_password:
            print(f"[Password Reset Email] ⚠️ SMTP設定がないため、開発モードで動作しています。")
            print(f"[Password Reset Email] パスワードリセットURL: {reset_url}")
            print(f"[Password Reset Email] ユーザー: {user.email}")
            return True
        
        # SMTP設定があるがエラーが発生した場合
        print(f"[Password Reset Email] SMTP設定を確認してください:")
        print(f"  - SMTP_SERVER: {smtp_server}")
        print(f"  - SMTP_PORT: {smtp_port}")
        print(f"  - SMTP_USERNAME: {smtp_username[:3]}***")
        print(f"[Password Reset Email] パスワードリセットURL（開発用）: {reset_url}")
        return False

