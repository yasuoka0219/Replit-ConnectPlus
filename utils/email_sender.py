"""
汎用的なメール送信ユーティリティ
顧客・取引先・連絡先へのメール送信に使用
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re


def send_email(to_email, subject, html_body, text_body=None):
    """
    汎用的なメール送信関数
    
    Args:
        to_email (str): 送信先メールアドレス
        subject (str): 件名
        html_body (str): HTML本文
        text_body (str, optional): テキスト本文（省略可）
        
    Returns:
        bool: 送信成功時True、失敗時False
    """
    try:
        # SMTP設定を取得
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '').strip()
        smtp_from_email = os.environ.get('SMTP_FROM_EMAIL', smtp_username)
        smtp_from_name = os.environ.get('SMTP_FROM_NAME', 'CONNECT+ CRM')
        
        # パスワードからスペースを削除
        if smtp_password:
            smtp_password = smtp_password.replace(' ', '')
        
        # SMTP設定がない場合
        if not smtp_username or not smtp_password:
            print(f"[Email] ⚠️ SMTP設定がありません。メール送信をスキップします。")
            print(f"[Email] 送信先: {to_email}")
            print(f"[Email] 件名: {subject}")
            return False
        
        # メールメッセージを作成
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'{smtp_from_name} <{smtp_from_email}>'
        msg['To'] = to_email
        
        # テキスト本文が指定されていない場合、HTMLから生成
        if not text_body:
            # 簡単なテキスト変換（HTMLタグを削除）
            text_body = re.sub('<[^<]+?>', '', html_body)
            text_body = text_body.strip()
        
        # メッセージを添付
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # SMTPサーバーに接続してメール送信（リトライとフォールバック付き）
        import time
        import ssl
        import socket
        
        # タイムアウトを5秒に短縮し、リトライを削減（Gunicornワーカータイムアウトを避けるため）
        connection_timeout = 5  # タイムアウトを5秒に短縮（Railwayの制限を考慮）
        
        # 最初のポートのみ試行（フォールバックを削除してタイムアウトを避ける）
        port = smtp_port
        last_error = None
        
        try:
            print(f"[Email] ポート {port} で接続中（タイムアウト: {connection_timeout}秒）...")
            
            # Port 465 uses SSL, port 587 uses STARTTLS
            if port == 465:
                # Use SMTP_SSL for port 465
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_server, port, timeout=connection_timeout, context=context) as server:
                    server.set_debuglevel(0)  # デバッグ情報を非表示（必要に応じて1に変更）
                    server.login(smtp_username, smtp_password)
                    server.send_message(msg)
            else:
                # Use SMTP with STARTTLS for port 587
                with smtplib.SMTP(smtp_server, port, timeout=connection_timeout) as server:
                    server.set_debuglevel(0)  # デバッグ情報を非表示（必要に応じて1に変更）
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.send_message(msg)
            
            print(f"[Email] ✓ メール送信成功: {to_email} (ポート {port})")
            import sys
            sys.stdout.flush()
            return True
            
        except (socket.error, OSError) as e:
            # Network errors - log and return False immediately
            last_error = e
            error_msg = f"[Email] ポート {port} で接続エラー: {e}"
            print(error_msg)
            import sys
            sys.stdout.flush()
            raise Exception(f"メール送信に失敗しました。エラー: {last_error}")
            
        except smtplib.SMTPAuthenticationError as e:
            # Authentication error - don't retry
            raise
            
        except smtplib.SMTPException as e:
            # SMTP error - log and raise immediately
            last_error = e
            error_msg = f"[Email] ポート {port} でSMTPエラー: {e}"
            print(error_msg)
            import sys
            sys.stdout.flush()
            raise Exception(f"メール送信に失敗しました。エラー: {last_error}")
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"[Email] ❌ SMTP認証エラー: {e}"
        print(error_msg)
        import sys
        import traceback
        print(f"[Email] エラー詳細:\n{traceback.format_exc()}")
        sys.stderr.write(f"{error_msg}\n")
        return False
        
    except smtplib.SMTPException as e:
        error_msg = f"[Email] ❌ SMTPエラー: {e}"
        print(error_msg)
        import sys
        import traceback
        print(f"[Email] エラー詳細:\n{traceback.format_exc()}")
        sys.stderr.write(f"{error_msg}\n")
        return False
        
    except Exception as e:
        error_msg = f"[Email] ❌ 予期しないエラー: {e}"
        print(error_msg)
        import sys
        import traceback
        print(f"[Email] エラー詳細:\n{traceback.format_exc()}")
        sys.stderr.write(f"{error_msg}\n")
        return False
