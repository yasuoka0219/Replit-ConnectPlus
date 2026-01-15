"""
SMTP設定をテストするスクリプト
メール送信機能が正しく動作するか確認します
"""
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 環境変数を読み込む
load_dotenv()

def test_smtp_connection():
    """SMTP接続をテストする"""
    print("=" * 60)
    print("SMTP設定テスト")
    print("=" * 60)
    
    # 環境変数を取得
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_username = os.environ.get('SMTP_USERNAME', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '').strip()
    smtp_from_email = os.environ.get('SMTP_FROM_EMAIL', smtp_username)
    smtp_from_name = os.environ.get('SMTP_FROM_NAME', 'CONNECT+ CRM')
    
    # パスワードからスペースを削除（Gmailアプリパスワードの場合）
    if smtp_password:
        smtp_password = smtp_password.replace(' ', '')
    
    print(f"\n📧 SMTP設定:")
    print(f"  サーバー: {smtp_server}")
    print(f"  ポート: {smtp_port}")
    print(f"  ユーザー名: {smtp_username[:3]}***" if smtp_username else "  ユーザー名: (未設定)")
    print(f"  パスワード: {'設定済み' if smtp_password else '(未設定)'}")
    print(f"  送信元メール: {smtp_from_email}")
    print(f"  送信元名: {smtp_from_name}")
    
    # SMTP設定の確認
    if not smtp_username or not smtp_password:
        print("\n❌ エラー: SMTP設定が不完全です")
        print("\n以下の環境変数を設定してください:")
        print("  SMTP_SERVER=smtp.gmail.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USERNAME=your-email@gmail.com")
        print("  SMTP_PASSWORD=your-app-password")
        print("  SMTP_FROM_EMAIL=your-email@gmail.com")
        print("  SMTP_FROM_NAME=CONNECT+ CRM")
        print("\n詳細は GMAIL_SMTP_SETUP.md を参照してください")
        return False
    
    # テストメールの送信先を入力
    print("\n" + "=" * 60)
    test_email = input("テストメールの送信先メールアドレスを入力してください: ").strip()
    
    if not test_email:
        print("❌ メールアドレスが入力されていません")
        return False
    
    # メール送信を試行
    try:
        print(f"\n📤 メール送信中...")
        print(f"  送信先: {test_email}")
        
        # メールメッセージを作成
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'CONNECT+ CRM - SMTP設定テスト'
        msg['From'] = f'{smtp_from_name} <{smtp_from_email}>'
        msg['To'] = test_email
        
        # HTML本文
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #4F46E5;">CONNECT+ CRM - SMTP設定テスト</h2>
              <p>このメールは、SMTP設定が正しく動作していることを確認するためのテストメールです。</p>
              <div style="background-color: #F3F4F6; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <p style="margin: 0; color: #059669; font-weight: bold;">✅ SMTP設定は正常に動作しています！</p>
              </div>
              <p style="color: #666; font-size: 14px;">
                このメールが届いたということは、メール送信機能が正しく設定されています。
              </p>
              <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
              <p style="color: #999; font-size: 12px;">
                このメールは CONNECT+ CRM から自動送信されています。
              </p>
            </div>
          </body>
        </html>
        """
        
        # テキスト本文
        text_body = """
CONNECT+ CRM - SMTP設定テスト

このメールは、SMTP設定が正しく動作していることを確認するためのテストメールです。

✅ SMTP設定は正常に動作しています！

このメールが届いたということは、メール送信機能が正しく設定されています。

---
このメールは CONNECT+ CRM から自動送信されています。
        """
        
        # メッセージを添付
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # SMTPサーバーに接続してメール送信
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.set_debuglevel(1)  # デバッグ情報を表示
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print("\n✅ メール送信成功！")
        print(f"   {test_email} にメールを送信しました")
        print("\n📬 メールボックスを確認してください（スパムフォルダも確認）")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ SMTP認証エラー: {e}")
        print("\n対処法:")
        print("  1. SMTP_USERNAMEとSMTP_PASSWORDが正しいか確認")
        print("  2. Gmailの場合、アプリパスワードを使用しているか確認")
        print("  3. 2段階認証が有効になっているか確認")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTPエラー: {e}")
        print("\n対処法:")
        print("  1. SMTP_SERVERとSMTP_PORTが正しいか確認")
        print("  2. ファイアウォールでポート587がブロックされていないか確認")
        return False
        
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        print(f"\nエラー詳細:\n{traceback.format_exc()}")
        return False

if __name__ == '__main__':
    test_smtp_connection()
