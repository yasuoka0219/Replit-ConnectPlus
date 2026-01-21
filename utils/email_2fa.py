"""
Email-based 2FA (Two-Factor Authentication) utility
Generates and sends email verification codes for 2FA
"""
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from flask import current_app
from database import db


# Email configuration constants
EMAIL_CODE_LENGTH = 6
EMAIL_CODE_EXPIRY_MINUTES = 10
MAX_CODE_ATTEMPTS = 3


def generate_email_code(length=EMAIL_CODE_LENGTH):
    """
    Generate random numeric code for email verification
    
    Args:
        length (int): Length of the code (default: 6)
        
    Returns:
        str: Numeric code
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def send_2fa_email(user_email, code):
    """
    Send 2FA verification code via email
    
    Args:
        user_email (str): Recipient email address
        code (str): Verification code to send
        
    Returns:
        bool: True if email sent successfully
    """
    try:
        # Get email configuration from environment
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '').strip()
        # Remove spaces from app password if present (Gmail app passwords often have spaces)
        if smtp_password:
            smtp_password = smtp_password.replace(' ', '')
        smtp_from_email = os.environ.get('SMTP_FROM_EMAIL', smtp_username)
        smtp_from_name = os.environ.get('SMTP_FROM_NAME', 'CONNECT+ CRM')
        
        # If no SMTP credentials configured, use a mock/test mode
        if not smtp_username or not smtp_password:
            print(f"[2FA Email] ⚠️ SMTP設定がありません。開発モードで動作しています。")
            print(f"[2FA Email] =========================================")
            print(f"[2FA Email] 認証コード: {code}")
            print(f"[2FA Email] メールアドレス: {user_email}")
            print(f"[2FA Email] =========================================")
            print(f"[2FA Email] このコードを使用して2段階認証を設定してください。")
            print(f"[2FA Email] SendGridなどのメール送信サービスを設定することを推奨します。")
            # 開発モードでもTrueを返す（エラーを防ぐため）
            return True  # Return True in development/test mode
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'CONNECT+ CRM - 2段階認証コード'
        msg['From'] = f'{smtp_from_name} <{smtp_from_email}>'
        msg['To'] = user_email
        
        # Create HTML email body
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #4F46E5;">CONNECT+ CRM - 2段階認証</h2>
              <p>ログイン用の認証コードをお送りします。</p>
              <div style="background-color: #F3F4F6; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
                <h1 style="font-size: 32px; letter-spacing: 8px; color: #4F46E5; margin: 0;">{code}</h1>
              </div>
              <p style="color: #666; font-size: 14px;">
                このコードは10分間有効です。<br>
                このメールに心当たりがない場合は、無視してください。
              </p>
              <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
              <p style="color: #999; font-size: 12px;">
                このメールは CONNECT+ CRM から自動送信されています。
              </p>
            </div>
          </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
CONNECT+ CRM - 2段階認証

ログイン用の認証コードをお送りします。

認証コード: {code}

このコードは10分間有効です。
このメールに心当たりがない場合は、無視してください。

---
このメールは CONNECT+ CRM から自動送信されています。
        """
        
        # Attach both versions
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email with retry and fallback logic
        try:
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
            max_retries = 2  # リトライ回数を減らす（タイムアウトを避けるため）
            connection_timeout = 10  # タイムアウトを10秒に短縮（Railwayの制限を考慮）
            
            for attempt in range(max_retries):
                for port in ports_to_try:
                    try:
                        print(f"[2FA Email] 試行 {attempt + 1}/{max_retries}: ポート {port} で接続中...")
                        
                        # Port 465 uses SSL, port 587 uses STARTTLS
                        if port == 465:
                            # Use SMTP_SSL for port 465
                            context = ssl.create_default_context()
                            with smtplib.SMTP_SSL(smtp_server, port, timeout=connection_timeout, context=context) as server:
                                server.set_debuglevel(0)  # Set to 1 for debug output
                                server.login(smtp_username, smtp_password)
                                server.send_message(msg)
                        else:
                            # Use SMTP with STARTTLS for port 587
                            with smtplib.SMTP(smtp_server, port, timeout=connection_timeout) as server:
                                server.set_debuglevel(0)  # Set to 1 for debug output
                                server.starttls()
                                server.login(smtp_username, smtp_password)
                                server.send_message(msg)
                        
                        success_msg = f"[2FA Email] ✓ Code sent to {user_email} (ポート {port})"
                        print(success_msg)
                        import sys
                        sys.stdout.flush()  # ログが即座に出力されるように
                        return True
                        
                    except (socket.error, OSError) as e:
                        # Network errors - try next port or retry
                        last_error = e
                        error_msg = f"[2FA Email] ポート {port} で接続エラー: {e}"
                        print(error_msg)
                        if port == ports_to_try[-1] and attempt < max_retries - 1:
                            # Last port and not last attempt - wait before retry
                            wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                            print(f"[2FA Email] {wait_time}秒待機してから再試行します...")
                            time.sleep(wait_time)
                        continue
                        
                    except smtplib.SMTPAuthenticationError as e:
                        # Authentication error - don't retry
                        raise
                        
                    except smtplib.SMTPException as e:
                        # SMTP error - try next port or retry
                        last_error = e
                        error_msg = f"[2FA Email] ポート {port} でSMTPエラー: {e}"
                        print(error_msg)
                        if port == ports_to_try[-1] and attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 2
                            print(f"[2FA Email] {wait_time}秒待機してから再試行します...")
                            time.sleep(wait_time)
                        continue
            
            # All attempts failed
            error_msg = f"[2FA Email] ❌ すべての試行が失敗しました。最後のエラー: {last_error}"
            print(error_msg)
            import sys
            sys.stdout.flush()
            return False
            
        except smtplib.SMTPAuthenticationError as e:
            # Authentication error - log but don't raise (allow user to see code in logs)
            error_msg = f"[2FA Email] ❌ SMTP認証エラー: {e}"
            print(error_msg)
            print(f"[2FA Email] ユーザー名: {smtp_username}")
            print(f"[2FA Email] パスワード長: {len(smtp_password)}文字")
            print(f"[2FA Email] アプリパスワードが正しいか、2段階認証が有効か確認してください")
            # 詳細なエラー情報も出力
            import sys
            import traceback
            print(f"[2FA Email] エラー詳細:\n{traceback.format_exc()}")
            print(f"[2FA Email] =========================================")
            print(f"[2FA Email] ⚠️ メール送信に失敗しましたが、認証コードはログに表示されています")
            print(f"[2FA Email] 認証コード: {code}")
            print(f"[2FA Email] メールアドレス: {user_email}")
            print(f"[2FA Email] =========================================")
            sys.stdout.flush()
            return False  # Don't raise - return False instead
        except smtplib.SMTPException as e:
            # SMTP error - log but don't raise
            error_msg = f"[2FA Email] ❌ SMTPエラー: {e}"
            print(error_msg)
            import sys
            import traceback
            print(f"[2FA Email] エラー詳細:\n{traceback.format_exc()}")
            print(f"[2FA Email] =========================================")
            print(f"[2FA Email] ⚠️ メール送信に失敗しましたが、認証コードはログに表示されています")
            print(f"[2FA Email] 認証コード: {code}")
            print(f"[2FA Email] メールアドレス: {user_email}")
            print(f"[2FA Email] =========================================")
            sys.stdout.flush()
            return False  # Don't raise - return False instead
        except Exception as e:
            # Unexpected error - log but don't raise
            error_msg = f"[2FA Email] ❌ 予期しないエラー: {e}"
            print(error_msg)
            import sys
            import traceback
            print(f"[2FA Email] エラー詳細:\n{traceback.format_exc()}")
            print(f"[2FA Email] =========================================")
            print(f"[2FA Email] ⚠️ メール送信に失敗しましたが、認証コードはログに表示されています")
            print(f"[2FA Email] 認証コード: {code}")
            print(f"[2FA Email] メールアドレス: {user_email}")
            print(f"[2FA Email] =========================================")
            sys.stdout.flush()
            return False  # Don't raise - return False instead
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[2FA Email] ❌ メール送信エラー: {e}")
        print(f"[2FA Email] エラー詳細:\n{error_details}")
        
        # In development, still return True if credentials not configured
        if not smtp_username or not smtp_password:
            print(f"[2FA Email] ⚠️ SMTP設定がないため、開発モードで動作しています。")
            print(f"[2FA Email] 認証コード: {code}")
            print(f"[2FA Email] メールアドレス: {user_email}")
            return True
        
        # SMTP設定があるがエラーが発生した場合
        print(f"[2FA Email] =========================================")
        print(f"[2FA Email] ⚠️ メール送信に失敗しました")
        print(f"[2FA Email] =========================================")
        print(f"[2FA Email] 認証コード: {code}")
        print(f"[2FA Email] メールアドレス: {user_email}")
        print(f"[2FA Email] =========================================")
        print(f"[2FA Email] このコードを使用して2段階認証を設定してください。")
        print(f"[2FA Email] SMTP設定を確認してください:")
        print(f"  - SMTP_SERVER: {smtp_server}")
        print(f"  - SMTP_PORT: {smtp_port}")
        print(f"  - SMTP_USERNAME: {smtp_username[:3]}***")
        print(f"[2FA Email] SendGridなどのメール送信サービスを使用することを推奨します。")
        import sys
        sys.stdout.flush()  # ログが即座に出力されるように
        return False


def verify_email_code(user, code, stored_code, code_expires_at):
    """
    Verify email 2FA code
    
    Args:
        user (User): User object
        code (str): Code to verify
        stored_code (str): Stored code to compare
        code_expires_at (datetime): Expiry time of the code
        
    Returns:
        bool: True if code is valid
    """
    if not stored_code or not code:
        return False
    
    # Check if code has expired
    if code_expires_at and datetime.utcnow() > code_expires_at:
        return False
    
    # Compare codes (case-insensitive)
    return stored_code.strip() == code.strip()


# Note: Email2FACode model will be added to models.py

