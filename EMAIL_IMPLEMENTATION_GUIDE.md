# メール送信機能実装ガイド

2段階認証メールの確認から、顧客・取引先・連絡先へのメール送信機能追加までの完全ガイドです。

## 📋 実装の流れ

1. **ステップ1**: 2段階認証メールが届くようにする（SMTP設定の確認）
2. **ステップ2**: 汎用的なメール送信機能を実装
3. **ステップ3**: 顧客・取引先・連絡先へのメール送信機能を追加

---

## 🔍 ステップ1: 2段階認証メールが届かない原因を確認

### 1-1. SMTP設定の確認

まず、SMTP設定が正しく行われているか確認します。

#### 環境変数の確認

本番環境で以下の環境変数が設定されているか確認してください：

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CONNECT+ CRM
```

#### SMTP設定のテスト

テストスクリプトを実行して、SMTP設定が正しく動作するか確認します：

```bash
python test_smtp.py
```

このスクリプトは：
- SMTP設定を確認
- テストメールを送信
- エラーがあれば詳細を表示

### 1-2. ログの確認

本番環境のログで、メール送信に関するエラーメッセージを確認してください：

```bash
# Railwayの場合
railway logs

# Renderの場合
# ダッシュボードの「Logs」タブ

# Herokuの場合
heroku logs --tail

# VPSの場合
sudo journalctl -u connectplus -f
```

確認すべきログメッセージ：

- ✅ `[2FA Email] ✓ Code sent to ...` → メール送信成功
- ❌ `[2FA Email] ⚠️ SMTP設定がありません` → SMTP設定が未設定
- ❌ `[2FA Email] ❌ SMTP認証エラー` → 認証情報が間違っている
- ❌ `[2FA Email] ❌ SMTPエラー` → 接続エラー

### 1-3. ログから認証コードを確認

メールが届かない場合でも、ログに認証コードが表示されます：

```
[2FA Email] 認証コード: 123456
```

このコードを使用して一時的に2段階認証を設定・ログインできます。

---

## 🛠️ ステップ2: 汎用的なメール送信機能を実装

2段階認証メールが届くようになったら、汎用的なメール送信機能を実装します。

### 2-1. メール送信ユーティリティの作成

`utils/email_sender.py` を作成します：

```python
"""
汎用的なメール送信ユーティリティ
顧客・取引先・連絡先へのメール送信に使用
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

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
            import re
            text_body = re.sub('<[^<]+?>', '', html_body)
            text_body = text_body.strip()
        
        # メッセージを添付
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # SMTPサーバーに接続してメール送信
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"[Email] ✓ メール送信成功: {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[Email] ❌ SMTP認証エラー: {e}")
        return False
        
    except smtplib.SMTPException as e:
        print(f"[Email] ❌ SMTPエラー: {e}")
        return False
        
    except Exception as e:
        print(f"[Email] ❌ 予期しないエラー: {e}")
        import traceback
        print(f"[Email] エラー詳細:\n{traceback.format_exc()}")
        return False
```

### 2-2. app.pyにインポート

`app.py`の上部に追加：

```python
from utils.email_sender import send_email
```

---

## 📧 ステップ3: 顧客・取引先・連絡先へのメール送信機能を追加

### 3-1. APIエンドポイントの追加

`app.py`に以下を追加：

```python
@app.route('/api/contacts/<int:contact_id>/send-email', methods=['POST'])
@login_required
def send_contact_email(contact_id):
    """連絡先にメールを送信"""
    contact = Contact.query.get_or_404(contact_id)
    
    if not contact.email:
        return jsonify({'success': False, 'error': '連絡先にメールアドレスが登録されていません'}), 400
    
    data = request.get_json()
    subject = data.get('subject', '')
    body = data.get('body', '')
    
    if not subject or not body:
        return jsonify({'success': False, 'error': '件名と本文を入力してください'}), 400
    
    # HTML本文を作成
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #4F46E5;">{subject}</h2>
          <div style="white-space: pre-wrap;">{body}</div>
          <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
          <p style="color: #999; font-size: 12px;">
            このメールは CONNECT+ CRM から送信されました。
          </p>
        </div>
      </body>
    </html>
    """
    
    # メール送信
    success = send_email(contact.email, subject, html_body, body)
    
    if success:
        # 活動履歴に記録
        activity = Activity(
            company_id=contact.company_id,
            user_id=current_user.id,
            type='email',
            title=f'メール送信: {subject}',
            body=body,
            happened_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'メールを送信しました'})
    else:
        return jsonify({'success': False, 'error': 'メールの送信に失敗しました'}), 500
```

### 3-2. 連絡先詳細画面にメール送信ボタンを追加

`templates/company_detail.html` の連絡先セクションに追加：

```html
<!-- メール送信モーダル -->
<div id="email-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full mx-4">
        <h3 class="text-xl font-bold mb-4">メール送信</h3>
        <form id="email-form">
            <input type="hidden" id="email-contact-id">
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">送信先</label>
                <input type="email" id="email-to" readonly class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-700">
            </div>
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">件名</label>
                <input type="text" id="email-subject" required class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600">
            </div>
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">本文</label>
                <textarea id="email-body" rows="10" required class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600"></textarea>
            </div>
            <div class="flex gap-2 justify-end">
                <button type="button" onclick="closeEmailModal()" class="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg">キャンセル</button>
                <button type="submit" class="px-4 py-2 bg-primary text-white rounded-lg">送信</button>
            </div>
        </form>
    </div>
</div>

<script>
function openEmailModal(contactId, contactEmail) {
    document.getElementById('email-contact-id').value = contactId;
    document.getElementById('email-to').value = contactEmail;
    document.getElementById('email-modal').classList.remove('hidden');
}

function closeEmailModal() {
    document.getElementById('email-modal').classList.add('hidden');
    document.getElementById('email-form').reset();
}

document.getElementById('email-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const contactId = document.getElementById('email-contact-id').value;
    const subject = document.getElementById('email-subject').value;
    const body = document.getElementById('email-body').value;
    
    try {
        const response = await fetch(`/api/contacts/${contactId}/send-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ subject, body })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('メールを送信しました');
            closeEmailModal();
            // 活動履歴を再読み込み
            loadActivities();
        } else {
            alert('エラー: ' + (data.error || 'メールの送信に失敗しました'));
        }
    } catch (error) {
        alert('通信エラーが発生しました');
    }
});
</script>
```

連絡先のメールアドレス表示部分を修正：

```html
{% if contact.email %}
<div class="col-span-2">
    📧 <a href="mailto:{{ contact.email }}" class="text-primary hover:underline">{{ contact.email }}</a>
    <button onclick="openEmailModal({{ contact.id }}, '{{ contact.email }}')" class="ml-2 px-2 py-1 text-sm bg-primary text-white rounded hover:bg-indigo-700">
        メール送信
    </button>
</div>
{% endif %}
```

---

## ✅ 実装完了後の確認

### 確認項目

1. **2段階認証メールが届く**
   - ログイン時にメールで認証コードを受信
   - 2段階認証設定時にメールで認証コードを受信

2. **連絡先へのメール送信ができる**
   - 連絡先詳細画面で「メール送信」ボタンをクリック
   - メール送信フォームが表示される
   - メールが送信される
   - 活動履歴に記録される

3. **エラーハンドリング**
   - SMTP設定がない場合、適切なエラーメッセージが表示される
   - メール送信失敗時、エラーメッセージが表示される

---

## 📚 参考資料

- [Gmail SMTP設定ガイド](./GMAIL_SMTP_SETUP.md)
- [本番環境メール機能実装手順](./PRODUCTION_EMAIL_SETUP.md)
- [他のユーザーへのメール送信機能について](./EMAIL_TO_OTHER_USERS.md)

---

## 🆘 トラブルシューティング

### 2段階認証メールが届かない

1. **SMTP設定を確認**
   ```bash
   python test_smtp.py
   ```

2. **ログを確認**
   - エラーメッセージを確認
   - 認証コードがログに表示されているか確認

3. **環境変数を再確認**
   - 本番環境で環境変数が正しく設定されているか
   - アプリケーションを再起動

### 連絡先へのメール送信が失敗する

1. **SMTP設定を確認**
   - 2段階認証メールが届くか確認
   - 同じSMTP設定を使用

2. **連絡先のメールアドレスを確認**
   - メールアドレスが正しく登録されているか
   - メールアドレスの形式が正しいか

3. **ログを確認**
   - エラーメッセージを確認
   - メール送信の詳細を確認

---

**実装を開始する前に、まず `python test_smtp.py` を実行してSMTP設定を確認してください！**
