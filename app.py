import os
from functools import wraps
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import hmac

# Python 3.9 compatibility: Custom password check function that avoids scrypt
def safe_check_password_hash(pwhash, password):
    """
    Check password hash safely, avoiding scrypt on Python 3.9.
    If the stored hash uses scrypt, we can't verify it - user needs to reset password.
    """
    # If the hash starts with scrypt, we can't verify it on Python 3.9
    if isinstance(pwhash, str) and pwhash.startswith('scrypt$'):
        return False
    
    try:
        return check_password_hash(pwhash, password)
    except (AttributeError, ValueError) as e:
        # Catch scrypt-related errors and return False
        if 'scrypt' in str(e).lower():
            return False
        # Re-raise other errors
        raise
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database import db
from models import User, Company, Contact, Deal, Task, Activity, Quote, QuoteItem, Invoice, InvoiceItem, OrgProfile, Team, LoginAttempt, SecurityLog, Email2FACode, GoogleCalendarConnection, PasswordResetToken
from utils.export_utils import (
    export_companies_to_csv, export_companies_to_excel,
    export_deals_to_csv, export_deals_to_excel,
    export_activities_to_csv, export_activities_to_excel
)
from utils.import_utils import (
    parse_csv_file, parse_excel_file,
    validate_company_row, validate_deal_row
)
from utils.security import (
    validate_password_strength, log_login_attempt, check_login_attempts,
    log_security_event, generate_2fa_secret, get_2fa_provisioning_uri,
    generate_2fa_qr_code, verify_2fa_code, generate_backup_codes,
    get_client_ip, get_user_agent
)
from utils.email_2fa import (
    generate_email_code, send_2fa_email, verify_email_code,
    EMAIL_CODE_EXPIRY_MINUTES
)
from utils.google_calendar import (
    get_authorization_url, exchange_code_for_tokens, get_calendar_service,
    create_calendar_event, update_calendar_event, delete_calendar_event,
    test_connection
)
from utils.password_reset import (
    generate_reset_token, send_password_reset_email,
    RESET_TOKEN_EXPIRY_HOURS
)

load_dotenv()

# Industry categories for company classification
INDUSTRY_CATEGORIES = [
    "製造業",
    "小売・卸売",
    "飲食・宿泊",
    "IT・ソフトウェア",
    "広告・メディア",
    "建設・不動産",
    "人材・教育",
    "医療・福祉",
    "金融・保険",
    "物流・運輸",
    "自治体・公共",
    "専門サービス",
    "エネルギー・インフラ",
    "エンタメ・スポーツ",
    "その他"
]

# Win/Loss reason categories (v2.6.0)
WIN_REASON_CATEGORIES = [
    "提案が課題に合致",
    "優位性が明確",
    "顧客理解が深い",
    "コストパフォーマンス",
    "条件（納期・支払）が柔軟",
    "担当対応を評価",
    "過去取引の信頼",
    "紹介・口コミ",
    "機能優位",
    "サポート体制優位",
    "品質・性能を高評価",
    "カスタマイズ性",
    "導入実績が豊富",
    "導入時期が一致",
    "予算化タイミングが合致",
    "展示会/セミナー効果",
    "Web/広告から好印象",
    "その他"
]

LOSS_REASON_CATEGORIES = [
    "価格が高い",
    "予算確保不可/削減",
    "検討延期",
    "他社決定が先行",
    "条件で劣後",
    "機能で劣後",
    "既存ベンダー継続",
    "課題と不一致",
    "期待とのギャップ",
    "顧客理解不足",
    "キーマン関係構築不足",
    "社内稟議通過不可",
    "検討中止",
    "組織変更・予算凍結",
    "担当者退職/異動",
    "提案スピード遅延",
    "フォロー不足",
    "見積・社内対応遅延",
    "その他"
]

ROLE_LABELS = {
    'admin': '管理者',
    'lead': 'リーダー',
    'member': 'メンバー',
    'viewer': '閲覧のみ'
}

TEAM_SCOPE_OPTIONS = ('all', 'team', 'personal')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

# PostgreSQL用の設定（SQLiteの場合は適用しない）
database_url = os.environ.get('DATABASE_URL', '')
if database_url and 'postgresql' in database_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 5,
        'max_overflow': 10,
        'echo_pool': False,
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 5,
            'keepalives_count': 3,
            'options': '-c statement_timeout=30000'
        }
    }
else:
    # SQLite用の設定
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'echo': False
    }

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'basic'  # セッション保護を基本レベルに


def has_role(user, *roles):
    return user.is_authenticated and user.role in roles


def is_team_manager(user):
    return has_role(user, 'admin', 'lead')


def can_import_export(user):
    return has_role(user, 'admin', 'lead')


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('権限が不足しています。', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def can_access_deal(deal):
    if not current_user.is_authenticated:
        return False
    if is_team_manager(current_user):
        return True
    if deal.assignee_id == current_user.id:
        return True
    if current_user.team_id and deal.team_id == current_user.team_id:
        return True
    return deal.team_id is None


@app.context_processor
def inject_role_context():
    return {
        'ROLE_LABELS': ROLE_LABELS,
        'current_team': current_user.team if current_user.is_authenticated else None,
        'is_team_manager': is_team_manager(current_user) if current_user.is_authenticated else False,
        'can_import_export': can_import_export(current_user) if current_user.is_authenticated else False,
        'has_role': lambda user, *roles: has_role(user, *roles) if user and user.is_authenticated else False
    }


def ensure_default_team():
    """Ensure at least one team exists and return it."""
    team = Team.query.order_by(Team.id.asc()).first()
    if not team:
        team = Team(name='メインチーム', description='自動作成された標準チーム')
        db.session.add(team)
        db.session.commit()
    return team


def ensure_import_export_permission(redirect_endpoint='dashboard'):
    if not current_user.is_authenticated or not can_import_export(current_user):
        flash('インポート/エクスポート権限がありません。', 'error')
        return redirect(url_for(redirect_endpoint))
    return None


def get_available_scopes(user):
    scopes = []
    if is_team_manager(user):
        scopes.append('all')
    if user.team_id:
        scopes.append('team')
    scopes.append('personal')
    # Remove duplicates while preserving order
    seen = set()
    ordered = []
    for scope in scopes:
        if scope not in seen:
            ordered.append(scope)
            seen.add(scope)
    return ordered


def resolve_view_scope(user, requested_scope):
    scopes = get_available_scopes(user)
    default_scope = 'team' if user.team_id else 'personal'
    if requested_scope in scopes:
        return requested_scope
    return default_scope


def apply_scope_to_query(query, user, view_scope):
    if view_scope == 'personal':
        return query.filter(Deal.assignee_id == user.id)
    if view_scope == 'team' and user.team_id:
        return query.filter(
            db.or_(
                Deal.team_id == user.team_id,
                Deal.team_id.is_(None)
            )
        )
    return query

@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access - clear session and redirect to login"""
    from flask import session
    session.clear()
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    """Load user from database"""
    try:
        user = db.session.get(User, int(user_id))
        if user is None:
            # User doesn't exist, clear session
            return None
        return user
    except (ValueError, TypeError):
        # Invalid user_id
        return None
    except Exception as e:
        db.session.rollback()
        print(f"Error loading user: {e}")
        return None

@app.errorhandler(Exception)
def handle_database_error(error):
    from werkzeug.exceptions import HTTPException
    # Don't interfere with HTTP exceptions (404, 500, etc.)
    if isinstance(error, HTTPException):
        return error
    # Handle database connection errors
    if "SSL SYSCALL error" in str(error) or "OperationalError" in str(error.__class__.__name__):
        db.session.rollback()
        db.session.remove()
        flash('データベース接続エラーが発生しました。再度お試しください。', 'error')
        return redirect(url_for('index'))
    raise error

@app.route('/')
def index():
    """Redirect to dashboard if authenticated, otherwise to login"""
    from flask_login import current_user
    from flask import session
    
    # セッションをチェックして、無効な場合はクリア
    try:
        if current_user and hasattr(current_user, 'is_authenticated'):
            if current_user.is_authenticated and current_user.id:
                # ユーザーが存在するか確認
                user = User.query.get(current_user.id)
                if user:
                    return redirect(url_for('dashboard'))
                else:
                    # ユーザーが存在しない場合はセッションをクリア
                    session.clear()
    except Exception:
        session.clear()
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - with security enhancements"""
    from flask import session
    from flask_login import current_user
    
    # 無効なセッションをクリア
    try:
        if current_user and hasattr(current_user, 'is_authenticated'):
            if current_user.is_authenticated:
                # ユーザーが実際に存在するか確認
                user = User.query.get(current_user.id) if hasattr(current_user, 'id') else None
                if user:
                    return redirect(url_for('dashboard'))
                else:
                    # ユーザーが存在しない場合はセッションをクリア
                    session.clear()
    except Exception:
        session.clear()
    
    if request.method == 'POST':
        # Get form data - check both regular field and hidden field (for 2FA)
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        two_factor_code = request.form.get('two_factor_code', '').strip() if request.form.get('two_factor_code') else None
        
        # Check if we're in the 2FA verification step (email already in session)
        is_2fa_verification_step = 'login_email' in session and session.get('login_email')
        
        # Validate input
        if not email and not is_2fa_verification_step:
            flash('メールアドレスを入力してください。', 'error')
            return render_template('login.html')
        
        # If we're in 2FA verification step, use email from session
        if is_2fa_verification_step:
            email = session.get('login_email')
        
        user = User.query.filter_by(email=email).first() if email else None
        
        # Check if account is locked (by failed attempts)
        if user and hasattr(user, 'is_locked') and user.is_locked():
            flash(f'アカウントがロックされています。しばらくしてから再試行してください。', 'error')
            log_login_attempt(email, False, user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
            return render_template('login.html', email=email)
        
        # Check login attempts (brute force protection) - using LoginAttempt table
        if email and not is_2fa_verification_step:
            is_locked, attempts_remaining = check_login_attempts(email)
            if is_locked:
                flash(f'アカウントが一時的にロックされています。15分後に再試行してください。', 'error')
                log_login_attempt(email, False, ip_address=get_client_ip(), user_agent=get_user_agent())
                return render_template('login.html', email=email)
        
        # If we're in 2FA verification step, skip password check and go directly to 2FA verification
        if is_2fa_verification_step:
            if not user:
                flash('ユーザーが見つかりませんでした。', 'error')
                session.pop('login_email', None)
                session.pop('login_code_id', None)
                return render_template('login.html')
            
            # Proceed to 2FA verification (password already verified in previous step)
            if user.two_factor_enabled:
                two_factor_type = 'email'  # Always use email-based 2FA
                
                if two_factor_code:
                    # Email-based 2FA verification
                    code_id = session.get('login_code_id')
                    if code_id:
                        email_code = Email2FACode.query.filter_by(
                            id=code_id,
                            user_id=user.id,
                            used=False
                        ).first()
                        
                        if email_code and email_code.is_valid():
                            if verify_email_code(user, two_factor_code, email_code.code, email_code.expires_at):
                                # Mark code as used
                                email_code.used = True
                                db.session.commit()
                                session.pop('login_email', None)
                                session.pop('login_code_id', None)
                                
                                # Successful login
                                login_user(user)
                                user.reset_failed_attempts()
                                user.unlock_account()
                                db.session.commit()
                                
                                log_login_attempt(email, True, user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
                                log_security_event('login', f'User {user.email} logged in', user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
                                
                                flash('ログインに成功しました！', 'success')
                                next_page = request.args.get('next')
                                return redirect(next_page if next_page else url_for('dashboard'))
                            else:
                                email_code.attempts += 1
                                db.session.commit()
                                flash('認証コードが正しくありません。', 'error')
                                log_login_attempt(email, False, user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
                                return render_template('login.html', two_factor_required=True, two_factor_type='email', email=email)
                        else:
                            flash('認証コードが期限切れです。再度コードを送信してください。', 'error')
                            session.pop('login_email', None)
                            session.pop('login_code_id', None)
                            return render_template('login.html', two_factor_required=True, two_factor_type='email', email=email)
                    else:
                        flash('認証コードが見つかりません。再度コードを送信してください。', 'error')
                        session.pop('login_email', None)
                        return render_template('login.html', two_factor_required=True, two_factor_type='email', email=email)
                else:
                    # 2FA required but code not provided - stay on 2FA page
                    return render_template('login.html', two_factor_required=True, two_factor_type='email', email=email)
            else:
                # 2FA not enabled but we're in verification step - clear session and show login form
                session.pop('login_email', None)
                session.pop('login_code_id', None)
                return render_template('login.html', email=email)
        
        # If we're in 2FA verification step, we've already handled it above, so skip password check
        # (This should never be reached if 2FA verification step is properly handled, but just in case)
        if is_2fa_verification_step:
            # Should have been handled above, but if we reach here, return 2FA page
            return render_template('login.html', two_factor_required=True, two_factor_type='email', email=email)
        
        # Validate password (not in 2FA verification step)
        if not password:
            flash('パスワードを入力してください。', 'error')
            return render_template('login.html', email=email)
        
        # Verify password (only if not in 2FA verification step)
        if user and password and user.password_hash and safe_check_password_hash(user.password_hash, password):
            # Password is correct, now check 2FA if enabled
            if user.two_factor_enabled:
                two_factor_type = 'email'  # Always use email-based 2FA
                
                # First step: password is correct, now request 2FA code
                session['login_email'] = email
                
                # Send email code
                code = generate_email_code()
                expires_at = datetime.utcnow() + timedelta(minutes=EMAIL_CODE_EXPIRY_MINUTES)
                
                # Invalidate old codes
                Email2FACode.query.filter_by(
                    user_id=user.id,
                    used=False
                ).update({'used': True})
                
                # Store new code
                email_code = Email2FACode(
                    user_id=user.id,
                    code=code,
                    expires_at=expires_at
                )
                db.session.add(email_code)
                db.session.commit()
                
                # Send email
                send_2fa_email(user.email, code)
                session['login_code_id'] = email_code.id
                
                flash('認証コードをメールで送信しました。メールに記載されている6桁のコードを入力してください。メールが届かない場合は、コンソールに認証コードが表示されています。', 'info')
                
                return render_template('login.html', two_factor_required=True, two_factor_type='email', email=email)
            
            # Successful login (2FA not enabled, or 2FA verified)
            login_user(user)
            user.reset_failed_attempts()
            user.unlock_account()
            db.session.commit()
            
            # Clear login session
            session.pop('login_email', None)
            
            log_login_attempt(email, True, user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
            log_security_event('login', f'User {user.email} logged in', user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
            
            flash('ログインに成功しました！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            # Failed login - password is incorrect
            if user:
                # Increment failed attempts
                user.increment_failed_attempts()
                current_attempts = user.failed_login_attempts
                db.session.commit()
                
                # Check if account should be locked
                if current_attempts >= 5:
                    user.lock_account(30)
                    db.session.commit()
                    flash('アカウントが30分間ロックされました。', 'error')
                else:
                    attempts_remaining = max(0, 5 - current_attempts)
                    flash(f'メールアドレスまたはパスワードが正しくありません。残り試行回数: {attempts_remaining}回', 'error')
            else:
                # User not found - don't reveal if email exists or not
                flash('メールアドレスまたはパスワードが正しくありません。', 'error')
            
            log_login_attempt(email, False, user.id if user else None, ip_address=get_client_ip(), user_agent=get_user_agent())
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validate password strength
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', name=name, email=email)
        
        # Check password confirmation
        if password != password_confirm:
            flash('パスワードが一致しません。', 'error')
            return render_template('register.html', name=name, email=email)
        
        if User.query.filter_by(email=email).first():
            flash('このメールアドレスは既に登録されています。', 'error')
            return render_template('register.html', name=name, email=email)
        
        total_users = User.query.count()
        role = 'admin' if total_users == 0 else 'member'
        team = ensure_default_team()

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role,
            team_id=team.id if team else None
        )
        
        db.session.add(user)
        db.session.commit()
        
        log_security_event('user_registered', f'New user {email} registered', user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
        
        flash('アカウントが作成されました！ログインしてください。', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """パスワードリセットリクエスト"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('メールアドレスを入力してください。', 'error')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        # セキュリティのため、ユーザーが存在しても存在しなくても同じメッセージを表示
        if user:
            # 古いトークンを無効化
            PasswordResetToken.query.filter_by(user_id=user.id, used=False).update({'used': True})
            db.session.commit()
            
            # 新しいトークンを生成
            token = generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRY_HOURS)
            
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(reset_token)
            db.session.commit()
            
            # リセットURLを生成
            reset_url = url_for('reset_password', token=token, _external=True)
            
            # メール送信
            send_password_reset_email(user, token, reset_url)
            
            log_security_event('password_reset_requested', f'Password reset requested for {email}', user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
        
        # セキュリティのため、ユーザーの有無に関わらず同じメッセージを表示
        flash('パスワードリセット用のメールを送信しました。メールをご確認ください。', 'info')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """パスワードリセット実行"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # トークンを検証
    reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
    
    if not reset_token or not reset_token.is_valid():
        flash('パスワードリセットリンクが無効または期限切れです。再度リクエストしてください。', 'error')
        return redirect(url_for('forgot_password'))
    
    user = reset_token.user
    
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        
        # パスワード検証
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('reset_password.html', token=token)
        
        if password != password_confirm:
            flash('パスワードが一致しません。', 'error')
            return render_template('reset_password.html', token=token)
        
        # パスワードを更新
        user.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        user.reset_failed_attempts()
        user.unlock_account()
        
        # トークンを無効化
        reset_token.used = True
        
        # 他の有効なリセットトークンも無効化
        PasswordResetToken.query.filter_by(user_id=user.id, used=False).update({'used': True})
        
        db.session.commit()
        
        log_security_event('password_reset_completed', f'Password reset completed for {user.email}', user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
        
        flash('パスワードを変更しました。新しいパスワードでログインしてください。', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

@app.route('/clear-session')
def clear_session():
    """Clear session and redirect to login - for fixing redirect loops"""
    from flask import session
    from flask_login import logout_user
    try:
        logout_user()
    except:
        pass
    session.clear()
    flash('セッションをクリアしました。再度ログインしてください。', 'info')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    # Log security event before logout
    log_security_event('logout', f'User {current_user.email} logged out', current_user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
    logout_user()
    flash('ログアウトしました。', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_companies = Company.query.count()
    total_contacts = Contact.query.count()
    total_deals = Deal.query.count()
    total_tasks = Task.query.count()
    
    deals_by_stage = db.session.query(
        Deal.stage, db.func.count(Deal.id)
    ).group_by(Deal.stage).all()
    
    deals_by_status = db.session.query(
        Deal.status, db.func.count(Deal.id)
    ).group_by(Deal.status).all()
    
    total_amount = db.session.query(db.func.sum(Deal.amount)).scalar() or 0
    
    recent_deals = Deal.query.order_by(Deal.created_at.desc()).limit(5).all()
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_companies=total_companies,
                         total_contacts=total_contacts,
                         total_deals=total_deals,
                         total_tasks=total_tasks,
                         deals_by_stage=deals_by_stage,
                         deals_by_status=deals_by_status,
                         total_amount=total_amount,
                         recent_deals=recent_deals,
                         recent_tasks=recent_tasks,
                         industries=INDUSTRY_CATEGORIES)

@app.route('/companies')
@login_required
def companies():
    from datetime import datetime, date, timedelta
    
    # 基本検索
    search = request.args.get('search', '')
    
    # 高度なフィルタ
    industry_filter = request.args.get('industry', '')
    heat_score_filter = request.args.get('heat_score', '')
    employee_min = request.args.get('employee_min', '')
    employee_max = request.args.get('employee_max', '')
    last_contact_filter = request.args.get('last_contact', '')
    tag_filter = request.args.get('tag', '')
    
    # ソート機能
    sort_by = request.args.get('sort_by', 'name')  # デフォルト: 企業名
    sort_order = request.args.get('sort_order', 'asc')  # デフォルト: 昇順（あいうえお順）
    
    query = Company.query
    
    # 基本検索
    if search:
        query = query.filter(
            db.or_(
                Company.name.ilike(f'%{search}%'),
                Company.industry.ilike(f'%{search}%'),
                Company.location.ilike(f'%{search}%')
            )
        )
    
    # 高度なフィルタ
    if industry_filter:
        query = query.filter(Company.industry == industry_filter)
    
    if heat_score_filter:
        try:
            heat_score = int(heat_score_filter)
            if 1 <= heat_score <= 5:
                query = query.filter(Company.heat_score == heat_score)
        except ValueError:
            pass
    
    if employee_min:
        try:
            query = query.filter(Company.employee_size >= int(employee_min))
        except ValueError:
            pass
    
    if employee_max:
        try:
            query = query.filter(Company.employee_size <= int(employee_max))
        except ValueError:
            pass
    
    if last_contact_filter:
        today = date.today()
        if last_contact_filter == '30days':
            cutoff_date = today - timedelta(days=30)
            query = query.filter(
                db.or_(
                    Company.last_contacted_at >= cutoff_date,
                    Company.last_contacted_at.is_(None)
                )
            )
        elif last_contact_filter == '60days':
            cutoff_date = today - timedelta(days=60)
            query = query.filter(
                db.or_(
                    Company.last_contacted_at >= cutoff_date,
                    Company.last_contacted_at.is_(None)
                )
            )
        elif last_contact_filter == '90days':
            cutoff_date = today - timedelta(days=90)
            query = query.filter(
                db.or_(
                    Company.last_contacted_at >= cutoff_date,
                    Company.last_contacted_at.is_(None)
                )
            )
        elif last_contact_filter == 'over90days':
            cutoff_date = today - timedelta(days=90)
            query = query.filter(
                db.and_(
                    Company.last_contacted_at < cutoff_date,
                    Company.last_contacted_at.isnot(None)
                )
            )
        elif last_contact_filter == 'never':
            query = query.filter(Company.last_contacted_at.is_(None))
    
    if tag_filter:
        # タグで検索（カンマ区切りのタグ文字列から検索）
        query = query.filter(Company.tags.ilike(f'%{tag_filter}%'))
    
    # ソート処理
    sort_column = None
    if sort_by == 'name':
        sort_column = Company.name
    elif sort_by == 'last_contact':
        sort_column = Company.last_contacted_at
    elif sort_by == 'heat_score':
        sort_column = Company.heat_score
    elif sort_by == 'deal_count':
        # 案件数でソート（関連テーブルをカウント）
        # 計算が必要なため、一旦ソートはスキップ（後でPythonでソート）
        pass
    
    if sort_column:
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        # デフォルトソート（企業名昇順）
        query = query.order_by(Company.name.asc())
    
    companies_list = query.all()
    
    # 案件数でソートする場合（Pythonでソート）
    if sort_by == 'deal_count':
        companies_list.sort(
            key=lambda c: len(c.deals) if hasattr(c, 'deals') else 0,
            reverse=(sort_order == 'desc')
        )
    
    return render_template('companies.html', 
                         companies=companies_list, 
                         search=search,
                         industry_filter=industry_filter,
                         heat_score_filter=heat_score_filter,
                         employee_min=employee_min,
                         employee_max=employee_max,
                         last_contact_filter=last_contact_filter,
                         tag_filter=tag_filter,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         industries=INDUSTRY_CATEGORIES)

@app.route('/companies/export')
@login_required
def export_companies():
    """企業データをCSV/Excelでエクスポート"""
    guard = ensure_import_export_permission('companies')
    if guard:
        return guard
    format_type = request.args.get('format', 'csv')  # csv or excel
    
    # 現在のフィルタ条件を適用（companies()と同じロジック）
    from datetime import datetime, date, timedelta
    
    search = request.args.get('search', '')
    industry_filter = request.args.get('industry', '')
    heat_score_filter = request.args.get('heat_score', '')
    employee_min = request.args.get('employee_min', '')
    employee_max = request.args.get('employee_max', '')
    last_contact_filter = request.args.get('last_contact', '')
    tag_filter = request.args.get('tag', '')
    
    query = Company.query
    
    # 基本検索
    if search:
        query = query.filter(
            db.or_(
                Company.name.ilike(f'%{search}%'),
                Company.industry.ilike(f'%{search}%'),
                Company.location.ilike(f'%{search}%')
            )
        )
    
    # 高度なフィルタ
    if industry_filter:
        query = query.filter(Company.industry == industry_filter)
    
    if heat_score_filter:
        try:
            heat_score = int(heat_score_filter)
            if 1 <= heat_score <= 5:
                query = query.filter(Company.heat_score == heat_score)
        except ValueError:
            pass
    
    if employee_min:
        try:
            query = query.filter(Company.employee_size >= int(employee_min))
        except ValueError:
            pass
    
    if employee_max:
        try:
            query = query.filter(Company.employee_size <= int(employee_max))
        except ValueError:
            pass
    
    if last_contact_filter:
        today = date.today()
        if last_contact_filter == '30days':
            cutoff_date = today - timedelta(days=30)
            query = query.filter(
                db.or_(
                    Company.last_contacted_at >= cutoff_date,
                    Company.last_contacted_at.is_(None)
                )
            )
        elif last_contact_filter == '60days':
            cutoff_date = today - timedelta(days=60)
            query = query.filter(
                db.or_(
                    Company.last_contacted_at >= cutoff_date,
                    Company.last_contacted_at.is_(None)
                )
            )
        elif last_contact_filter == '90days':
            cutoff_date = today - timedelta(days=90)
            query = query.filter(
                db.or_(
                    Company.last_contacted_at >= cutoff_date,
                    Company.last_contacted_at.is_(None)
                )
            )
        elif last_contact_filter == 'over90days':
            cutoff_date = today - timedelta(days=90)
            query = query.filter(
                db.and_(
                    Company.last_contacted_at < cutoff_date,
                    Company.last_contacted_at.isnot(None)
                )
            )
        elif last_contact_filter == 'never':
            query = query.filter(Company.last_contacted_at.is_(None))
    
    if tag_filter:
        query = query.filter(Company.tags.ilike(f'%{tag_filter}%'))
    
    companies_list = query.all()
    
    # ファイル名に現在の日時を含める
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == 'excel':
        excel_file = export_companies_to_excel(companies_list)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'企業一覧_{timestamp}.xlsx'
        )
    else:
        csv_data = export_companies_to_csv(companies_list)
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=企業一覧_{timestamp}.csv'
        return response

@app.route('/companies/import', methods=['GET', 'POST'])
@login_required
def import_companies():
    """企業データのCSV/Excelインポート"""
    guard = ensure_import_export_permission('companies')
    if guard:
        return guard
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルが選択されていません。', 'error')
            return redirect(url_for('companies'))
        
        file = request.files['file']
        if file.filename == '':
            flash('ファイルが選択されていません。', 'error')
            return redirect(url_for('companies'))
        
        # ファイル拡張子を確認
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in ['csv', 'xlsx', 'xls']:
            flash('CSVまたはExcelファイルを選択してください。', 'error')
            return redirect(url_for('companies'))
        
        try:
            # ファイルをパース
            if file_ext == 'csv':
                rows = parse_csv_file(file)
            else:
                rows = parse_excel_file(file)
            
            if not rows:
                flash('データが含まれていません。', 'error')
                return redirect(url_for('companies'))
            
            # データをインポート
            success_count = 0
            error_count = 0
            errors = []
            
            for idx, row in enumerate(rows, start=2):  # 行番号は2から（ヘッダーを考慮）
                # バリデーション
                validation_errors = validate_company_row(row, idx, INDUSTRY_CATEGORIES)
                if validation_errors:
                    errors.extend(validation_errors)
                    error_count += 1
                    continue
                
                # 企業名を取得（日本語または英語ヘッダーに対応）
                company_name = row.get('企業名') or row.get('name', '').strip()
                if not company_name:
                    errors.append(f"行{idx}: 企業名が空です")
                    error_count += 1
                    continue
                
                # 既存の企業をチェック（重複はスキップ）
                existing_company = Company.query.filter_by(name=company_name).first()
                if existing_company:
                    # 重複は警告として記録するが、エラーカウントには含めない（スキップ）
                    errors.append(f"行{idx}: 企業 '{company_name}' は既に存在するためスキップしました")
                    continue  # エラーカウントを増やさず、この行をスキップ
                
                # 業界名を取得して正規化（バリデーションで正規化済みの場合はそれを使用）
                industry_raw = row.get('業界') or row.get('industry', '')
                industry = row.get('_normalized_industry')  # バリデーションで正規化された業界名を使用
                
                if not industry and industry_raw:
                    from utils.import_utils import normalize_industry_name
                    industry = normalize_industry_name(industry_raw)
                    # 正規化後の業界名が有効な業界カテゴリに含まれていない場合はNoneにする
                    if industry not in INDUSTRY_CATEGORIES:
                        industry = None
                
                # マッピングが適用された場合は警告として記録
                if row.get('_industry_mapped') and industry_raw:
                    errors.append(f"行{idx}: 業界 '{industry_raw}' を '{industry}' に変換しました")
                
                # 新しい企業を作成
                try:
                    company = Company(
                        name=company_name,
                        industry=industry,
                        location=row.get('所在地') or row.get('location', '') or None,
                        hq_location=row.get('本社所在地') or row.get('hq_location', '') or None,
                        employee_size=int(row.get('従業員数') or row.get('employee_size', '')) if row.get('従業員数') or row.get('employee_size') else None,
                        website=row.get('ウェブサイト') or row.get('website', '') or None,
                        heat_score=int(row.get('温度感スコア') or row.get('heat_score', '')) if row.get('温度感スコア') or row.get('heat_score') else None,
                        tags=row.get('タグ') or row.get('tags', '') or None,
                        memo=row.get('メモ') or row.get('memo', '') or None,
                        needs=row.get('ニーズ') or row.get('needs', '') or None,
                        kpi_current=row.get('現状KPI') or row.get('kpi_current', '') or None
                    )
                    
                    db.session.add(company)
                    success_count += 1
                except Exception as e:
                    errors.append(f"行{idx}: エラー - {str(e)}")
                    error_count += 1
            
            db.session.commit()
            
            # 結果メッセージ
            if success_count > 0:
                flash(f'{success_count}件の企業をインポートしました。', 'success')
            
            # 警告（重複やスキップされた行、マッピング）とエラーを分けて表示
            warnings = [e for e in errors if 'スキップ' in e or '変換しました' in e]
            actual_errors = [e for e in errors if e not in warnings]
            
            if warnings:
                warning_msg = f'{len(warnings)}件の警告: ' + '; '.join(warnings[:3])
                if len(warnings) > 3:
                    warning_msg += f' ... 他{len(warnings) - 3}件'
                flash(warning_msg, 'warning')
            
            if actual_errors:
                error_msg = f'{len(actual_errors)}件のエラーが発生しました。'
                error_msg += ' 詳細: ' + '; '.join(actual_errors[:5])  # 最初の5件のみ表示
                if len(actual_errors) > 5:
                    error_msg += f' ... 他{len(actual_errors) - 5}件'
                flash(error_msg, 'error')
            elif error_count > 0 and not actual_errors:
                # エラーカウントはあるが、実際のエラーがない場合（重複のみ）
                flash(f'{len(warnings)}件の行をスキップしました（重複または警告のみ）。', 'info')
            
            return redirect(url_for('companies'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'インポート中にエラーが発生しました: {str(e)}', 'error')
            return redirect(url_for('companies'))
    
    return render_template('import_companies.html')

@app.route('/companies/create', methods=['GET', 'POST'])
@login_required
def create_company():
    if request.method == 'POST':
        # Validate industry selection
        industry = request.form.get('industry')
        if industry and industry not in INDUSTRY_CATEGORIES:
            flash('無効な業界が選択されています。', 'error')
            return render_template('company_form.html', company=None, industries=INDUSTRY_CATEGORIES)
        
        company = Company(
            name=request.form.get('name'),
            industry=industry if industry else None,
            location=request.form.get('location'),
            memo=request.form.get('memo')
        )
        db.session.add(company)
        db.session.commit()
        flash('企業を追加しました。', 'success')
        return redirect(url_for('companies'))
    
    return render_template('company_form.html', company=None, industries=INDUSTRY_CATEGORIES)

@app.route('/companies/<int:id>')
@login_required
def view_company(id):
    """View company detail page with tabs for deals, contacts, activities"""
    company = Company.query.get_or_404(id)
    deals = Deal.query.filter_by(company_id=id).all()
    contacts = Contact.query.filter_by(company_id=id).all()
    
    return render_template('company_detail.html', 
                         company=company,
                         deals=deals,
                         contacts=contacts)

@app.route('/companies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_company(id):
    company = Company.query.get_or_404(id)
    
    if request.method == 'POST':
        # Validate industry selection
        industry = request.form.get('industry')
        if industry and industry not in INDUSTRY_CATEGORIES:
            flash('無効な業界が選択されています。', 'error')
            return render_template('company_form.html', company=company, industries=INDUSTRY_CATEGORIES)
        
        company.name = request.form.get('name')
        company.industry = industry if industry else None
        company.location = request.form.get('location')
        company.memo = request.form.get('memo')
        db.session.commit()
        flash('企業情報を更新しました。', 'success')
        return redirect(url_for('view_company', id=id))
    
    return render_template('company_form.html', company=company, industries=INDUSTRY_CATEGORIES)

@app.route('/companies/<int:id>/delete', methods=['POST'])
@login_required
def delete_company(id):
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash('企業を削除しました。', 'success')
    return redirect(url_for('companies'))

@app.route('/contacts')
@login_required
def contacts():
    search = request.args.get('search', '')
    
    # ソート機能
    sort_by = request.args.get('sort_by', 'name')  # デフォルト: 名前
    sort_order = request.args.get('sort_order', 'asc')  # デフォルト: 昇順（あいうえお順）
    
    if search:
        query = Contact.query.join(Company).filter(
            db.or_(
                Contact.name.ilike(f'%{search}%'),
                Contact.email.ilike(f'%{search}%'),
                Company.name.ilike(f'%{search}%')
            )
        )
    else:
        query = Contact.query.join(Company)
    
    # ソート処理
    sort_column = None
    if sort_by == 'name':
        sort_column = Contact.name
    elif sort_by == 'company_name':
        sort_column = Company.name
    
    if sort_column:
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        # デフォルトソート（名前昇順）
        query = query.order_by(Contact.name.asc())
    
    contacts_list = query.all()
    
    return render_template('contacts.html', 
                         contacts=contacts_list, 
                         search=search,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/contacts/create', methods=['GET', 'POST'])
@login_required
def create_contact():
    if request.method == 'POST':
        contact = Contact(
            company_id=request.form.get('company_id'),
            name=request.form.get('name'),
            title=request.form.get('title'),
            email=request.form.get('email'),
            phone=request.form.get('phone')
        )
        db.session.add(contact)
        db.session.commit()
        flash('連絡先を追加しました。', 'success')
        return redirect(url_for('contacts'))
    
    companies = Company.query.all()
    return render_template('contact_form.html', contact=None, companies=companies)

@app.route('/contacts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    contact = Contact.query.get_or_404(id)
    
    if request.method == 'POST':
        contact.company_id = request.form.get('company_id')
        contact.name = request.form.get('name')
        contact.title = request.form.get('title')
        contact.email = request.form.get('email')
        contact.phone = request.form.get('phone')
        db.session.commit()
        flash('連絡先情報を更新しました。', 'success')
        return redirect(url_for('contacts'))
    
    companies = Company.query.all()
    return render_template('contact_form.html', contact=contact, companies=companies)

@app.route('/contacts/<int:id>/delete', methods=['POST'])
@login_required
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('連絡先を削除しました。', 'success')
    return redirect(url_for('contacts'))

@app.route('/deals')
@login_required
def deals():
    from datetime import datetime, date
    
    # 基本検索・フィルタ
    search = request.args.get('search', '')
    stage_filter = request.args.get('stage', '')
    status_filter = request.args.get('status', '')
    assignee_filter = request.args.get('assignee', '')
    
    # 高度なフィルタ
    heat_score_filter = request.args.get('heat_score', '')
    amount_min = request.args.get('amount_min', '')
    amount_max = request.args.get('amount_max', '')
    created_from = request.args.get('created_from', '')
    created_to = request.args.get('created_to', '')
    revenue_month = request.args.get('revenue_month', '')
    
    # ソート機能
    sort_by = request.args.get('sort_by', 'created_at')  # デフォルト: 作成日
    sort_order = request.args.get('sort_order', 'desc')  # デフォルト: 降順（新着順）
    requested_scope = request.args.get('view_scope', None)
    view_scope = resolve_view_scope(current_user, requested_scope)
    
    query = Deal.query.join(Company)
    query = apply_scope_to_query(query, current_user, view_scope)
    
    # 基本検索
    if search:
        query = query.filter(
            db.or_(
                Deal.title.ilike(f'%{search}%'),
                Company.name.ilike(f'%{search}%')
            )
        )
    
    # 基本フィルタ
    if stage_filter:
        query = query.filter(Deal.stage == stage_filter)
    
    if status_filter:
        query = query.filter(Deal.status == status_filter)
    
    if assignee_filter:
        query = query.filter(Deal.assignee_id == int(assignee_filter))
    
    # 高度なフィルタ
    if heat_score_filter:
        query = query.filter(Deal.heat_score == heat_score_filter)
    
    if amount_min:
        try:
            query = query.filter(Deal.amount >= float(amount_min))
        except ValueError:
            pass
    
    if amount_max:
        try:
            query = query.filter(Deal.amount <= float(amount_max))
        except ValueError:
            pass
    
    if created_from:
        try:
            from_date = datetime.strptime(created_from, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Deal.created_at) >= from_date)
        except ValueError:
            pass
    
    if created_to:
        try:
            to_date = datetime.strptime(created_to, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Deal.created_at) <= to_date)
        except ValueError:
            pass
    
    if revenue_month:
        # 計上月フィルタ（YYYY-MM形式）- SQLiteとPostgreSQLの両方に対応
        try:
            year, month = map(int, revenue_month.split('-'))
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            is_postgres = 'postgresql' in db_url if db_url else False
            
            if is_postgres:
                # PostgreSQL: use to_char
                query = query.filter(
                    Deal.status == 'WON',
                    db.func.to_char(Deal.closed_at, 'YYYY-MM') == revenue_month
                )
            else:
                # SQLite: use strftime
                query = query.filter(
                    Deal.status == 'WON',
                    db.func.strftime('%Y-%m', Deal.closed_at) == revenue_month
                )
        except (ValueError, AttributeError):
            pass
    
    # ソート処理
    sort_column = None
    if sort_by == 'created_at':
        sort_column = Deal.created_at
    elif sort_by == 'updated_at':
        sort_column = Deal.updated_at
    elif sort_by == 'amount':
        sort_column = Deal.amount
    elif sort_by == 'title':
        sort_column = Deal.title
    elif sort_by == 'stage_days':
        # ステージ滞留日数（現在日時 - stage_entered_at）
        # 計算が必要なため、一旦ソートはスキップ（後でPythonでソート）
        pass
    
    if sort_column:
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    else:
        # デフォルトソート（作成日降順）
        query = query.order_by(Deal.created_at.desc())
    
    deals_list = query.all()
    
    # ステージ滞留日数でソートする場合（Pythonでソート）
    if sort_by == 'stage_days':
        today = datetime.now()
        deals_list.sort(
            key=lambda d: (today - d.stage_entered_at).days if d.stage_entered_at else 0,
            reverse=(sort_order == 'desc')
        )
    
    # Get users for filter dropdown
    users_query = User.query.order_by(User.name)
    if not is_team_manager(current_user):
        if current_user.team_id:
            users_query = users_query.filter(User.team_id == current_user.team_id)
        else:
            users_query = users_query.filter(User.id == current_user.id)
    users = users_query.all()
    
    return render_template('deals.html', 
                         deals=deals_list, 
                         search=search,
                         stage_filter=stage_filter, 
                         status_filter=status_filter,
                         assignee_filter=assignee_filter,
                         heat_score_filter=heat_score_filter,
                         amount_min=amount_min,
                         amount_max=amount_max,
                         created_from=created_from,
                         created_to=created_to,
                         revenue_month=revenue_month,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         users=users,
                         view_scope=view_scope,
                         available_scopes=get_available_scopes(current_user),
                         win_reasons=WIN_REASON_CATEGORIES, 
                         loss_reasons=LOSS_REASON_CATEGORIES)

@app.route('/deals/export')
@login_required
def export_deals():
    """案件データをCSV/Excelでエクスポート"""
    guard = ensure_import_export_permission('deals')
    if guard:
        return guard
    format_type = request.args.get('format', 'csv')  # csv or excel
    
    # 現在のフィルタ条件を適用（deals()と同じロジック）
    from datetime import datetime, date
    
    search = request.args.get('search', '')
    stage_filter = request.args.get('stage', '')
    status_filter = request.args.get('status', '')
    assignee_filter = request.args.get('assignee', '')
    heat_score_filter = request.args.get('heat_score', '')
    amount_min = request.args.get('amount_min', '')
    amount_max = request.args.get('amount_max', '')
    created_from = request.args.get('created_from', '')
    created_to = request.args.get('created_to', '')
    revenue_month = request.args.get('revenue_month', '')
    requested_scope = request.args.get('view_scope', None)
    view_scope = resolve_view_scope(current_user, requested_scope)
    
    query = Deal.query.join(Company)
    query = apply_scope_to_query(query, current_user, view_scope)
    
    if search:
        query = query.filter(
            db.or_(
                Deal.title.ilike(f'%{search}%'),
                Company.name.ilike(f'%{search}%')
            )
        )
    
    if stage_filter:
        query = query.filter(Deal.stage == stage_filter)
    
    if status_filter:
        query = query.filter(Deal.status == status_filter)
    
    if assignee_filter:
        query = query.filter(Deal.assignee_id == int(assignee_filter))
    
    if heat_score_filter:
        query = query.filter(Deal.heat_score == heat_score_filter)
    
    if amount_min:
        try:
            query = query.filter(Deal.amount >= float(amount_min))
        except ValueError:
            pass
    
    if amount_max:
        try:
            query = query.filter(Deal.amount <= float(amount_max))
        except ValueError:
            pass
    
    if created_from:
        try:
            from_date = datetime.strptime(created_from, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Deal.created_at) >= from_date)
        except ValueError:
            pass
    
    if created_to:
        try:
            to_date = datetime.strptime(created_to, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Deal.created_at) <= to_date)
        except ValueError:
            pass
    
    if revenue_month:
        try:
            year, month = map(int, revenue_month.split('-'))
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            is_postgres = 'postgresql' in db_url if db_url else False
            
            if is_postgres:
                query = query.filter(
                    Deal.status == 'WON',
                    db.func.to_char(Deal.closed_at, 'YYYY-MM') == revenue_month
                )
            else:
                query = query.filter(
                    Deal.status == 'WON',
                    db.func.strftime('%Y-%m', Deal.closed_at) == revenue_month
                )
        except (ValueError, AttributeError):
            pass
    
    deals_list = query.all()
    
    # ファイル名に現在の日時を含める
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == 'excel':
        excel_file = export_deals_to_excel(deals_list)
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'案件一覧_{timestamp}.xlsx'
        )
    else:
        csv_data = export_deals_to_csv(deals_list)
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=案件一覧_{timestamp}.csv'
        return response

@app.route('/deals/import', methods=['GET', 'POST'])
@login_required
def import_deals():
    """案件データのCSV/Excelインポート"""
    guard = ensure_import_export_permission('deals')
    if guard:
        return guard
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルが選択されていません。', 'error')
            return redirect(url_for('deals'))
        
        file = request.files['file']
        if file.filename == '':
            flash('ファイルが選択されていません。', 'error')
            return redirect(url_for('deals'))
        
        # ファイル拡張子を確認
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in ['csv', 'xlsx', 'xls']:
            flash('CSVまたはExcelファイルを選択してください。', 'error')
            return redirect(url_for('deals'))
        
        try:
            # ファイルをパース
            if file_ext == 'csv':
                rows = parse_csv_file(file)
            else:
                rows = parse_excel_file(file)
            
            if not rows:
                flash('データが含まれていません。', 'error')
                return redirect(url_for('deals'))
            
            # 企業名のマッピングを作成（企業名 → Companyオブジェクト）
            companies_dict = {}
            for company in Company.query.all():
                companies_dict[company.name] = company
            
            # データをインポート
            success_count = 0
            error_count = 0
            errors = []
            
            for idx, row in enumerate(rows, start=2):  # 行番号は2から
                # バリデーション
                validation_errors = validate_deal_row(row, idx, companies_dict)
                if validation_errors:
                    errors.extend(validation_errors)
                    error_count += 1
                    continue
                
                # 必須フィールドを取得
                company_name = row.get('企業名') or row.get('company_name', '').strip()
                deal_title = row.get('案件名') or row.get('title', '').strip()
                
                if not company_name or not deal_title:
                    errors.append(f"行{idx}: 企業名と案件名は必須です")
                    error_count += 1
                    continue
                
                company = companies_dict.get(company_name)
                if not company:
                    errors.append(f"行{idx}: 企業 '{company_name}' が見つかりません")
                    error_count += 1
                    continue
                
                # 新しい案件を作成
                try:
                    # ステータスの変換
                    status = row.get('ステータス') or row.get('status', 'OPEN')
                    status_map = {'進行中': 'OPEN', '受注': 'WON', '失注': 'LOST', '成約': 'WON'}
                    if status in status_map:
                        status = status_map[status]
                    
                    # 日付のパース
                    appointment_date = None
                    if row.get('アポイント日') or row.get('appointment_date'):
                        try:
                            date_str = row.get('アポイント日') or row.get('appointment_date', '')
                            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        except (ValueError, AttributeError):
                            pass
                    
                    closed_at = None
                    if row.get('クローズ日') or row.get('closed_at'):
                        try:
                            closed_str = row.get('クローズ日') or row.get('closed_at', '')
                            if len(closed_str) > 10:
                                closed_at = datetime.strptime(closed_str, '%Y-%m-%d %H:%M:%S')
                            else:
                                closed_at = datetime.strptime(closed_str, '%Y-%m-%d')
                        except (ValueError, AttributeError):
                            pass
                    
                    team_id = current_user.team_id
                    deal = Deal(
                        company_id=company.id,
                        title=deal_title,
                        stage=row.get('ステージ') or row.get('stage', '初回接触'),
                        amount=float(row.get('金額') or row.get('amount', 0)) if row.get('金額') or row.get('amount') else 0,
                        status=status,
                        heat_score=row.get('温度感スコア') or row.get('heat_score', 'C'),
                        assignee=row.get('担当者') or row.get('assignee', '') or None,
                        appointment_date=appointment_date,
                        next_action=row.get('次回アクション') or row.get('next_action', '') or None,
                        win_reason_category=row.get('受注理由カテゴリ') or row.get('win_reason_category', '') or None,
                        win_reason_detail=row.get('受注理由詳細') or row.get('win_reason_detail', '') or None,
                        lost_reason_category=row.get('失注理由カテゴリ') or row.get('lost_reason_category', '') or None,
                        lost_reason_detail=row.get('失注理由詳細') or row.get('lost_reason_detail', '') or None,
                        closed_at=closed_at,
                        note=row.get('メモ') or row.get('note', '') or None,
                        meeting_minutes=row.get('議事録') or row.get('meeting_minutes', '') or None,
                        team_id=team_id
                    )
                    
                    # 担当者IDを設定（担当者名から検索）
                    assignee_name = row.get('担当者') or row.get('assignee', '')
                    if assignee_name:
                        user = User.query.filter_by(name=assignee_name).first()
                        if user:
                            deal.assignee_id = user.id
                            deal.team_id = user.team_id or deal.team_id
                    
                    db.session.add(deal)
                    success_count += 1
                except Exception as e:
                    errors.append(f"行{idx}: エラー - {str(e)}")
                    error_count += 1
            
            db.session.commit()
            
            # 結果メッセージ
            if success_count > 0:
                flash(f'{success_count}件の案件をインポートしました。', 'success')
            if error_count > 0:
                error_msg = f'{error_count}件のエラーが発生しました。'
                if errors:
                    error_msg += ' 詳細: ' + '; '.join(errors[:5])
                    if len(errors) > 5:
                        error_msg += f' ... 他{len(errors) - 5}件'
                flash(error_msg, 'error')
            
            return redirect(url_for('deals'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'インポート中にエラーが発生しました: {str(e)}', 'error')
            return redirect(url_for('deals'))
    
    companies = Company.query.order_by(Company.name).all()
    return render_template('import_deals.html', companies=companies)

@app.route('/deals/create', methods=['GET', 'POST'])
@login_required
def create_deal():
    if request.method == 'POST':
        # Parse appointment date
        appointment_date = None
        appointment_date_str = request.form.get('appointment_date')
        if appointment_date_str:
            try:
                appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        status = request.form.get('status')
        
        # Set closed_at if status is WON or LOST
        closed_at = None
        if status in ['WON', 'LOST']:
            closed_at = datetime.utcnow()
        
        # Parse assignee_id
        assignee_id = request.form.get('assignee_id')
        assignee_id = int(assignee_id) if assignee_id and assignee_id != '' else None
        
        # Parse team_id (default to current user's team if not specified)
        team_id = request.form.get('team_id')
        team_id = int(team_id) if team_id and team_id != '' else (current_user.team_id if current_user.team_id else None)
        
        deal = Deal(
            company_id=request.form.get('company_id'),
            title=request.form.get('title'),
            stage=request.form.get('stage'),
            amount=float(request.form.get('amount', 0)),
            status=status,
            heat_score=request.form.get('heat_score', 'C'),
            note=request.form.get('note'),
            meeting_minutes=request.form.get('meeting_minutes'),
            next_action=request.form.get('next_action'),
            appointment_date=appointment_date,
            stage_entered_at=datetime.utcnow(),
            closed_at=closed_at,
            assignee_id=assignee_id,
            team_id=team_id
        )
        
        # Set win/loss reasons
        if status == 'WON':
            deal.win_reason_category = request.form.get('win_reason_category') or None
            deal.win_reason_detail = request.form.get('win_reason_detail') or None
        elif status == 'LOST':
            deal.lost_reason_category = request.form.get('lost_reason_category') or None
            deal.lost_reason_detail = request.form.get('lost_reason_detail') or None
        
        db.session.add(deal)
        db.session.commit()
        flash('案件を追加しました。', 'success')
        return redirect(url_for('deals'))
    
    companies = Company.query.all()
    users = User.query.order_by(User.name).all()
    teams = Team.query.order_by(Team.name).all()
    return render_template('deal_form.html', deal=None, companies=companies, users=users, teams=teams,
                         win_reasons=WIN_REASON_CATEGORIES, loss_reasons=LOSS_REASON_CATEGORIES)

@app.route('/deals/<int:id>')
@login_required
def view_deal(id):
    """View deal details with related quotes and invoices"""
    deal = Deal.query.get_or_404(id)
    company = Company.query.get_or_404(deal.company_id)
    
    # Get related quotes and invoices
    quotes = Quote.query.filter_by(deal_id=id).order_by(Quote.created_at.desc()).all()
    invoices = Invoice.query.filter_by(deal_id=id).order_by(Invoice.created_at.desc()).all()
    
    return render_template('deal_detail.html', deal=deal, company=company, quotes=quotes, invoices=invoices)

@app.route('/deals/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_deal(id):
    deal = Deal.query.get_or_404(id)
    
    if request.method == 'POST':
        # Check if stage has changed - update stage_entered_at if so
        new_stage = request.form.get('stage')
        if deal.stage != new_stage:
            deal.stage_entered_at = datetime.utcnow()
        
        # Parse appointment date
        appointment_date = None
        appointment_date_str = request.form.get('appointment_date')
        if appointment_date_str:
            try:
                appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        new_status = request.form.get('status')
        
        # Set closed_at if status changed to WON or LOST
        if new_status in ['WON', 'LOST'] and deal.status not in ['WON', 'LOST']:
            deal.closed_at = datetime.utcnow()
        # Clear closed_at if status changed back to OPEN
        elif new_status == 'OPEN' and deal.status in ['WON', 'LOST']:
            deal.closed_at = None
            deal.win_reason_category = None
            deal.win_reason_detail = None
            deal.lost_reason_category = None
            deal.lost_reason_detail = None
        
        deal.company_id = request.form.get('company_id')
        deal.title = request.form.get('title')
        deal.stage = new_stage
        deal.amount = float(request.form.get('amount', 0))
        deal.status = new_status
        deal.heat_score = request.form.get('heat_score', 'C')
        deal.note = request.form.get('note')
        deal.meeting_minutes = request.form.get('meeting_minutes')
        deal.next_action = request.form.get('next_action')
        deal.appointment_date = appointment_date
        
        # Parse and set assignee_id
        assignee_id = request.form.get('assignee_id')
        deal.assignee_id = int(assignee_id) if assignee_id and assignee_id != '' else None
        
        # Parse and set team_id
        team_id = request.form.get('team_id')
        deal.team_id = int(team_id) if team_id and team_id != '' else None
        
        # Set win/loss reasons
        if new_status == 'WON':
            deal.win_reason_category = request.form.get('win_reason_category') or None
            deal.win_reason_detail = request.form.get('win_reason_detail') or None
            # Clear lost reason
            deal.lost_reason_category = None
            deal.lost_reason_detail = None
        elif new_status == 'LOST':
            deal.lost_reason_category = request.form.get('lost_reason_category') or None
            deal.lost_reason_detail = request.form.get('lost_reason_detail') or None
            # Clear win reason
            deal.win_reason_category = None
            deal.win_reason_detail = None
        
        db.session.commit()
        flash('案件情報を更新しました。', 'success')
        return redirect(url_for('deals'))
    
    companies = Company.query.all()
    users = User.query.order_by(User.name).all()
    teams = Team.query.order_by(Team.name).all()
    return render_template('deal_form.html', deal=deal, companies=companies, users=users, teams=teams,
                         win_reasons=WIN_REASON_CATEGORIES, loss_reasons=LOSS_REASON_CATEGORIES)

@app.route('/deals/<int:id>/delete', methods=['POST'])
@login_required
def delete_deal(id):
    deal = Deal.query.get_or_404(id)
    db.session.delete(deal)
    db.session.commit()
    flash('案件を削除しました。', 'success')
    return redirect(url_for('deals'))

@app.route('/tasks')
@login_required
def tasks():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    query = Task.query
    
    if search:
        query = query.filter(
            db.or_(
                Task.title.ilike(f'%{search}%'),
                Task.deal_name.ilike(f'%{search}%')
            )
        )
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    tasks_list = query.order_by(Task.created_at.desc()).all()
    
    return render_template('tasks.html', tasks=tasks_list, search=search, 
                         status_filter=status_filter)

@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        task = Task(
            deal_name=request.form.get('deal_name'),
            title=request.form.get('title'),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
            status=request.form.get('status'),
            assignee=request.form.get('assignee')
        )
        db.session.add(task)
        db.session.commit()
        
        # Sync to Google Calendar if connected and due_date is set
        if task.due_date:
            connection = GoogleCalendarConnection.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).first()
            
            if connection:
                try:
                    # Convert date to datetime (start at 9:00 AM, end at 10:00 AM)
                    start_datetime = datetime.combine(task.due_date, datetime.min.time().replace(hour=9))
                    end_datetime = datetime.combine(task.due_date, datetime.min.time().replace(hour=10))
                    
                    event = create_calendar_event(
                        user_id=current_user.id,
                        title=task.title,
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        description=f"タスク: {task.deal_name or '関連案件なし'}" if task.deal_name else "タスク",
                        calendar_id=connection.calendar_id or 'primary'
                    )
                    
                    if event:
                        task.google_calendar_event_id = event.get('id')
                        db.session.commit()
                        flash('タスクを追加しました。Googleカレンダーにも同期しました。', 'success')
                    else:
                        flash('タスクを追加しました。', 'success')
                except Exception as e:
                    print(f"Error syncing task to Google Calendar: {e}")
                    flash('タスクを追加しました。（カレンダー同期でエラーが発生しました）', 'success')
            else:
                flash('タスクを追加しました。', 'success')
        else:
            flash('タスクを追加しました。', 'success')
        
        return redirect(url_for('tasks'))
    
    return render_template('task_form.html', task=None)

@app.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    
    if request.method == 'POST':
        old_due_date = task.due_date
        old_title = task.title
        
        task.deal_name = request.form.get('deal_name')
        task.title = request.form.get('title')
        task.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None
        task.status = request.form.get('status')
        task.assignee = request.form.get('assignee')
        db.session.commit()
        
        # Sync to Google Calendar if connected
        connection = GoogleCalendarConnection.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).first()
        
        if connection and task.google_calendar_event_id:
            try:
                if task.due_date:
                    start_datetime = datetime.combine(task.due_date, datetime.min.time().replace(hour=9))
                    end_datetime = datetime.combine(task.due_date, datetime.min.time().replace(hour=10))
                    
                    update_calendar_event(
                        user_id=current_user.id,
                        event_id=task.google_calendar_event_id,
                        title=task.title,
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        description=f"タスク: {task.deal_name or '関連案件なし'}" if task.deal_name else "タスク",
                        calendar_id=connection.calendar_id or 'primary'
                    )
                    flash('タスク情報を更新しました。Googleカレンダーも更新しました。', 'success')
                else:
                    # Delete calendar event if due_date is removed
                    delete_calendar_event(current_user.id, task.google_calendar_event_id, connection.calendar_id or 'primary')
                    task.google_calendar_event_id = None
                    db.session.commit()
                    flash('タスク情報を更新しました。Googleカレンダーから削除しました。', 'success')
            except Exception as e:
                print(f"Error updating calendar event: {e}")
                flash('タスク情報を更新しました。（カレンダー更新でエラーが発生しました）', 'success')
        elif connection and task.due_date and not task.google_calendar_event_id:
            # Create new calendar event if due_date is added
            try:
                start_datetime = datetime.combine(task.due_date, datetime.min.time().replace(hour=9))
                end_datetime = datetime.combine(task.due_date, datetime.min.time().replace(hour=10))
                
                event = create_calendar_event(
                    user_id=current_user.id,
                    title=task.title,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    description=f"タスク: {task.deal_name or '関連案件なし'}" if task.deal_name else "タスク",
                    calendar_id=connection.calendar_id or 'primary'
                )
                
                if event:
                    task.google_calendar_event_id = event.get('id')
                    db.session.commit()
                    flash('タスク情報を更新しました。Googleカレンダーにも追加しました。', 'success')
                else:
                    flash('タスク情報を更新しました。', 'success')
            except Exception as e:
                print(f"Error creating calendar event: {e}")
                flash('タスク情報を更新しました。（カレンダー追加でエラーが発生しました）', 'success')
        else:
            flash('タスク情報を更新しました。', 'success')
        
        return redirect(url_for('tasks'))
    
    deals_list = Deal.query.all()
    return render_template('task_form.html', task=task, deals=deals_list)

@app.route('/tasks/<int:id>/delete', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    
    # Delete from Google Calendar if connected
    connection = GoogleCalendarConnection.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).first()
    
    if connection and task.google_calendar_event_id:
        try:
            delete_calendar_event(current_user.id, task.google_calendar_event_id, connection.calendar_id or 'primary')
        except Exception as e:
            print(f"Error deleting calendar event: {e}")
    
    db.session.delete(task)
    db.session.commit()
    flash('タスクを削除しました。', 'success')
    return redirect(url_for('tasks'))

@app.route('/teams')
@login_required
def teams():
    """チーム管理ページ（全ユーザーが閲覧可能、編集は管理者・リーダーのみ）"""
    teams_list = Team.query.order_by(Team.created_at.desc()).all()
    users_list = User.query.order_by(User.name).all()
    
    return render_template('teams.html', teams=teams_list, users=users_list)

@app.route('/teams/create', methods=['POST'])
@login_required
def create_team():
    """チーム作成（管理者・リーダーのみ）"""
    if not is_team_manager(current_user):
        flash('チーム作成には管理者またはリーダー権限が必要です。', 'error')
        return redirect(url_for('teams'))
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    color = request.form.get('color', '')
    
    if not name:
        flash('チーム名は必須です。', 'error')
        return redirect(url_for('teams'))
    
    if Team.query.filter_by(name=name).first():
        flash('このチーム名は既に使用されています。', 'error')
        return redirect(url_for('teams'))
    
    team = Team(name=name, description=description or None, color=color or None)
    db.session.add(team)
    db.session.commit()
    
    flash('チームを作成しました。', 'success')
    return redirect(url_for('teams'))

@app.route('/teams/<int:id>/edit', methods=['POST'])
@login_required
def edit_team(id):
    """チーム編集（管理者・リーダーのみ）"""
    if not is_team_manager(current_user):
        flash('チーム編集には管理者またはリーダー権限が必要です。', 'error')
        return redirect(url_for('teams'))
    
    team = Team.query.get_or_404(id)
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    color = request.form.get('color', '')
    
    if not name:
        flash('チーム名は必須です。', 'error')
        return redirect(url_for('teams'))
    
    # 名前の重複チェック（自分自身は除外）
    existing = Team.query.filter_by(name=name).first()
    if existing and existing.id != team.id:
        flash('このチーム名は既に使用されています。', 'error')
        return redirect(url_for('teams'))
    
    team.name = name
    team.description = description or None
    team.color = color or None
    
    db.session.commit()
    flash('チーム情報を更新しました。', 'success')
    return redirect(url_for('teams'))

@app.route('/teams/<int:id>/delete', methods=['POST'])
@login_required
def delete_team(id):
    """チーム削除（管理者のみ）"""
    if not has_role(current_user, 'admin'):
        flash('チーム削除には管理者権限が必要です。', 'error')
        return redirect(url_for('teams'))
    
    team = Team.query.get_or_404(id)
    
    # デフォルトチームは削除不可
    if team.name == 'メインチーム':
        flash('デフォルトチームは削除できません。', 'error')
        return redirect(url_for('teams'))
    
    # チームに所属するユーザーをデフォルトチームに移動
    default_team = Team.query.filter_by(name='メインチーム').first()
    if default_team:
        User.query.filter_by(team_id=id).update({'team_id': default_team.id})
        Deal.query.filter_by(team_id=id).update({'team_id': default_team.id})
    
    db.session.delete(team)
    db.session.commit()
    
    flash('チームを削除しました。', 'success')
    return redirect(url_for('teams'))

@app.route('/teams/<int:team_id>/members', methods=['POST'])
@login_required
def update_team_members(team_id):
    """チームメンバー更新（管理者・リーダーのみ）"""
    if not is_team_manager(current_user):
        flash('メンバー管理には管理者またはリーダー権限が必要です。', 'error')
        return redirect(url_for('teams'))
    
    team = Team.query.get_or_404(team_id)
    
    # フォームから送信されたメンバーIDのリストを取得
    member_ids = request.form.getlist('members')
    
    try:
        # 選択されたメンバーをチームに割り当て
        for user_id in member_ids:
            user = User.query.get(int(user_id))
            if user:
                user.team_id = team_id
        
        # 選択されていないメンバーをチームから外す（管理者は除外）
        all_team_members = User.query.filter_by(team_id=team_id).all()
        for user in all_team_members:
            if str(user.id) not in member_ids and user.role != 'admin':
                user.team_id = None
        
        db.session.commit()
        flash('チームメンバーを更新しました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'メンバー更新中にエラーが発生しました: {str(e)}', 'error')
    
    return redirect(url_for('teams'))

@app.route('/teams/<int:team_id>/member/<int:user_id>/role', methods=['POST'])
@login_required
def update_member_role(team_id, user_id):
    """チームメンバーの役職を更新（管理者・リーダーのみ）"""
    if not is_team_manager(current_user):
        flash('役職変更には管理者またはリーダー権限が必要です。', 'error')
        return redirect(url_for('teams'))
    
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', 'member')
    
    # 管理者は管理者のみ変更可能
    if user.role == 'admin' and current_user.role != 'admin':
        flash('管理者の役職は変更できません。', 'error')
        return redirect(url_for('teams'))
    
    if new_role not in ['admin', 'lead', 'member', 'viewer']:
        flash('無効な役職です。', 'error')
        return redirect(url_for('teams'))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'{user.name}の役職を{new_role}に変更しました。', 'success')
    return redirect(url_for('teams'))

@app.route('/api/teams/<int:team_id>/members')
@login_required
def get_team_members(team_id):
    """チームに紐づくメンバー一覧を取得（全ユーザー閲覧可能）"""
    team = Team.query.get_or_404(team_id)
    
    members = []
    for user in team.users:
        members.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        })
    
    return jsonify({
        'success': True,
        'team_id': team_id,
        'team_name': team.name,
        'members': members
    })

@app.route('/api/teams/<int:team_id>/deals')
@login_required
def get_team_deals(team_id):
    """チームに紐づく案件一覧を取得（全ユーザー閲覧可能）"""
    
    team = Team.query.get_or_404(team_id)
    deals = Deal.query.filter_by(team_id=team_id).order_by(Deal.created_at.desc()).all()
    
    deals_data = []
    for deal in deals:
        deals_data.append({
            'id': deal.id,
            'title': deal.title,
            'company_name': deal.company.name if deal.company else None,
            'stage': deal.stage,
            'status': deal.status,
            'amount': deal.amount,
            'assignee_name': deal.get_assignee_name() if hasattr(deal, 'get_assignee_name') else None,
            'created_at': deal.created_at.isoformat() if deal.created_at else None
        })
    
    return jsonify({
        'success': True,
        'deals': deals_data,
        'team_name': team.name
    })

@app.route('/settings')
@login_required
def settings():
    org_profile = OrgProfile.query.first()
    return render_template('settings.html', org_profile=org_profile)


# 2FA (Two-Factor Authentication) Routes
@app.route('/settings/2fa')
@login_required
def settings_2fa():
    """2FA settings page"""
    user = current_user
    qr_code_data = None
    backup_codes = None
    email_code_id = None
    
    # Get the latest unused email code ID for this user
    if not user.two_factor_enabled:
        email_code = Email2FACode.query.filter_by(
            user_id=user.id,
            used=False
        ).order_by(Email2FACode.created_at.desc()).first()
        
        if email_code and email_code.is_valid():
            email_code_id = email_code.id
    
    if user.two_factor_secret and not user.two_factor_enabled:
        # Generate QR code for setup
        provisioning_uri = get_2fa_provisioning_uri(user)
        if provisioning_uri:
            qr_code_data = generate_2fa_qr_code(provisioning_uri)
    
    if user.two_factor_backup_codes:
        import json
        try:
            backup_codes = json.loads(user.two_factor_backup_codes)
        except:
            backup_codes = []
    
    return render_template('settings_2fa.html', 
                         two_factor_enabled=user.two_factor_enabled,
                         two_factor_type='email',  # Always use email-based 2FA
                         qr_code_data=None,  # No QR code for email-based 2FA
                         backup_codes=backup_codes,
                         email_code_id=email_code_id)


@app.route('/api/2fa/setup', methods=['POST'])
@login_required
def setup_2fa():
    """Setup 2FA - enable email 2FA"""
    try:
        data = request.get_json() or {}
        two_factor_type = 'email'  # Always use email-based 2FA
        
        user = current_user
        
        if user.two_factor_enabled:
            return jsonify({'success': False, 'error': '2FAは既に有効です'}), 400
        
        # Email-based 2FA setup
        user.two_factor_type = 'email'
        db.session.commit()
        
        # Send test email with verification code
        code = generate_email_code()
        expires_at = datetime.utcnow() + timedelta(minutes=EMAIL_CODE_EXPIRY_MINUTES)
        
        # Store code in database
        email_code = Email2FACode(
            user_id=user.id,
            code=code,
            expires_at=expires_at
        )
        db.session.add(email_code)
        db.session.commit()
        
        # Send email
        email_sent = send_2fa_email(user.email, code)
        
        if email_sent:
            log_security_event('2fa_setup_initiated', f'User {user.email} initiated email 2FA setup', user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
            
            # Check if SMTP is configured for message
            message = '認証コードをメールで送信しました。メールに記載されている6桁のコードを入力してください。'
            smtp_username = os.environ.get('SMTP_USERNAME', '')
            smtp_password = os.environ.get('SMTP_PASSWORD', '')
            if not smtp_username or not smtp_password:
                message += '（メールが届かない場合、サーバーのコンソールに認証コードが表示されています）'
            
            return jsonify({
                'success': True,
                'type': 'email',
                'message': message,
                'code_id': email_code.id  # For verification
            })
        else:
            db.session.delete(email_code)
            db.session.commit()
            return jsonify({'success': False, 'error': 'メールの送信に失敗しました。SMTP設定を確認してください。コンソールに認証コードが表示されている場合は、そのコードを使用してください。'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/2fa/verify', methods=['POST'])
@login_required
def verify_2fa():
    """Verify 2FA code and enable 2FA"""
    try:
        data = request.get_json()
        code = data.get('code')
        code_id = data.get('code_id')  # For email-based 2FA
        
        if not code:
            return jsonify({'success': False, 'error': '認証コードが必要です'}), 400
        
        user = current_user
        
        # Always use email-based 2FA verification
        if not code_id:
            return jsonify({'success': False, 'error': 'コードIDが必要です'}), 400
        
        email_code = Email2FACode.query.filter_by(
            id=code_id,
            user_id=user.id,
            used=False
        ).first()
        
        if not email_code or not email_code.is_valid():
            return jsonify({'success': False, 'error': '認証コードが無効または期限切れです。再度コードを送信してください。'}), 400
        
        # Verify code
        if verify_email_code(user, code, email_code.code, email_code.expires_at):
            # Mark code as used
            email_code.used = True
            email_code.attempts += 1
            
            # Enable 2FA
            user.two_factor_enabled = True
            db.session.commit()
            
            log_security_event('2fa_enabled', f'User {user.email} enabled email-based 2FA', user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
            
            return jsonify({'success': True, 'message': '2FAが有効になりました'})
        else:
            # Increment attempts
            email_code.attempts += 1
            db.session.commit()
            
            if email_code.attempts >= 3:
                return jsonify({'success': False, 'error': '認証コードの試行回数が上限に達しました。再度コードを送信してください。'}), 400
            else:
                return jsonify({'success': False, 'error': '認証コードが正しくありません'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/2fa/send-email-code', methods=['POST'])
@login_required
def send_email_2fa_code():
    """Send email 2FA code (for login or setup)"""
    try:
        user = current_user
        
        if user.two_factor_type != 'email':
            return jsonify({'success': False, 'error': 'メール認証が設定されていません'}), 400
        
        # Generate and send code
        code = generate_email_code()
        expires_at = datetime.utcnow() + timedelta(minutes=EMAIL_CODE_EXPIRY_MINUTES)
        
        # Invalidate old codes
        Email2FACode.query.filter_by(
            user_id=user.id,
            used=False
        ).update({'used': True})
        
        # Store new code
        email_code = Email2FACode(
            user_id=user.id,
            code=code,
            expires_at=expires_at
        )
        db.session.add(email_code)
        db.session.commit()
        
        # Send email
        email_sent = send_2fa_email(user.email, code)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': '認証コードをメールで送信しました。',
                'code_id': email_code.id
            })
        else:
            return jsonify({'success': False, 'error': 'メールの送信に失敗しました。'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/login/send-email-code', methods=['POST'])
def send_login_email_code():
    """Send email 2FA code during login (public endpoint)"""
    try:
        email = request.json.get('email') if request.is_json else request.form.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'メールアドレスが必要です'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.two_factor_enabled or user.two_factor_type != 'email':
            return jsonify({'success': False, 'error': 'メール認証が設定されていません'}), 400
        
        # Generate and send code
        code = generate_email_code()
        expires_at = datetime.utcnow() + timedelta(minutes=EMAIL_CODE_EXPIRY_MINUTES)
        
        # Invalidate old codes
        Email2FACode.query.filter_by(
            user_id=user.id,
            used=False
        ).update({'used': True})
        
        # Store new code
        email_code = Email2FACode(
            user_id=user.id,
            code=code,
            expires_at=expires_at
        )
        db.session.add(email_code)
        db.session.commit()
        
        # Send email
        email_sent = send_2fa_email(user.email, code)
        
        if email_sent:
            # Store code_id in session for verification
            session['login_code_id'] = email_code.id
            return jsonify({
                'success': True,
                'message': '認証コードをメールで送信しました。',
                'code_id': email_code.id
            })
        else:
            return jsonify({'success': False, 'error': 'メールの送信に失敗しました。'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """Disable 2FA"""
    try:
        data = request.get_json()
        code = data.get('code')
        password = data.get('password')
        
        user = current_user
        
        if not user.two_factor_enabled:
            return jsonify({'success': False, 'error': '2FAは既に無効です'}), 400
        
        # Verify password
        if not safe_check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'error': 'パスワードが正しくありません'}), 400
        
        # No need to verify 2FA code when disabling (only password required)
        
        # Disable 2FA
        user.two_factor_enabled = False
        user.two_factor_type = None
        user.two_factor_secret = None
        user.two_factor_backup_codes = None
        
        # Invalidate email codes
        Email2FACode.query.filter_by(
            user_id=user.id,
            used=False
        ).update({'used': True})
        
        db.session.commit()
        
        log_security_event('2fa_disabled', f'User {user.email} disabled 2FA', user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
        
        return jsonify({'success': True, 'message': '2FAが無効になりました'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# Security Logs Route
@app.route('/settings/security-logs')
@login_required
@role_required('admin')
def security_logs():
    """Security logs page (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    event_type = request.args.get('event_type', '')
    user_id = request.args.get('user_id', type=int)
    
    query = SecurityLog.query.order_by(SecurityLog.created_at.desc())
    
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    if user_id:
        query = query.filter(SecurityLog.user_id == user_id)
    
    logs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('security_logs.html', logs=logs, event_type=event_type, user_id=user_id)


# Google Calendar Integration Routes
@app.route('/settings/calendar')
@login_required
def settings_calendar():
    """Google Calendar integration settings page"""
    connection = GoogleCalendarConnection.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).first()
    
    is_connected = connection is not None
    connection_status = {
        'connected': is_connected,
        'connected_at': connection.connected_at if connection else None,
        'last_sync_at': connection.last_sync_at if connection else None
    }
    
    return render_template('settings_calendar.html', connection_status=connection_status)


@app.route('/auth/google')
@login_required
def google_auth():
    """Initiate Google OAuth flow"""
    try:
        authorization_url, state = get_authorization_url()
        # Store state in session for verification
        from flask import session
        session['google_oauth_state'] = state
        return redirect(authorization_url)
    except ValueError as e:
        flash(f'Googleカレンダー連携の設定が不完全です: {str(e)}', 'error')
        return redirect(url_for('settings_calendar'))
    except Exception as e:
        flash(f'認証エラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('settings_calendar'))


@app.route('/auth/google/callback')
@login_required
def google_auth_callback():
    """Handle Google OAuth callback"""
    from flask import session
    
    # Verify state
    state = request.args.get('state')
    stored_state = session.get('google_oauth_state')
    
    if not state or state != stored_state:
        flash('認証エラー: セキュリティ検証に失敗しました', 'error')
        return redirect(url_for('settings_calendar'))
    
    # Clear state from session
    session.pop('google_oauth_state', None)
    
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f'認証がキャンセルされました: {error}', 'error')
        return redirect(url_for('settings_calendar'))
    
    if not code:
        flash('認証コードが取得できませんでした', 'error')
        return redirect(url_for('settings_calendar'))
    
    try:
        # Exchange code for tokens
        credentials = exchange_code_for_tokens(code, state)
        
        # Save connection to database
        connection = GoogleCalendarConnection.query.filter_by(
            user_id=current_user.id
        ).first()
        
        if connection:
            # Update existing connection
            connection.access_token = credentials['token']
            connection.refresh_token = credentials.get('refresh_token') or connection.refresh_token
            connection.token_expiry = credentials.get('expiry')
            connection.is_active = True
            connection.connected_at = datetime.utcnow()
        else:
            # Create new connection
            connection = GoogleCalendarConnection(
                user_id=current_user.id,
                access_token=credentials['token'],
                refresh_token=credentials.get('refresh_token'),
                token_expiry=credentials.get('expiry'),
                is_active=True
            )
            db.session.add(connection)
        
        db.session.commit()
        
        # Test connection
        if test_connection(current_user.id):
            log_security_event('google_calendar_connected', f'User {current_user.email} connected Google Calendar', current_user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
            flash('Googleカレンダーとの連携が完了しました', 'success')
        else:
            flash('Googleカレンダーとの接続に失敗しました。もう一度お試しください', 'error')
        
        return redirect(url_for('settings_calendar'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'認証処理中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('settings_calendar'))


@app.route('/api/calendar/disconnect', methods=['POST'])
@login_required
def disconnect_calendar():
    """Disconnect Google Calendar"""
    try:
        connection = GoogleCalendarConnection.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).first()
        
        if connection:
            connection.is_active = False
            db.session.commit()
            
            log_security_event('google_calendar_disconnected', f'User {current_user.email} disconnected Google Calendar', current_user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
            
            return jsonify({'success': True, 'message': 'Googleカレンダーとの連携を解除しました'})
        else:
            return jsonify({'success': False, 'error': '連携が見つかりませんでした'}), 404
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/calendar/test', methods=['POST'])
@login_required
def test_calendar_connection():
    """Test Google Calendar connection"""
    try:
        if test_connection(current_user.id):
            return jsonify({'success': True, 'message': 'Googleカレンダーとの接続が正常です'})
        else:
            return jsonify({'success': False, 'error': 'Googleカレンダーとの接続に失敗しました'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/org-profile', methods=['GET'])
@login_required
def get_org_profile():
    """Get organization profile"""
    profile = OrgProfile.query.first()
    if not profile:
        return jsonify({'success': True, 'profile': None})
    
    return jsonify({
        'success': True,
        'profile': {
            'org_name': profile.org_name,
            'org_name_kana': profile.org_name_kana,
            'postal_code': profile.postal_code,
            'address': profile.address,
            'phone': profile.phone,
            'email': profile.email,
            'representative': profile.representative,
            'registration_number': profile.registration_number
        }
    })

@app.route('/api/org-profile', methods=['POST', 'PUT'])
@login_required
def save_org_profile():
    """Create or update organization profile"""
    try:
        data = request.get_json()
        profile = OrgProfile.query.first()
        
        if not profile:
            profile = OrgProfile()
            db.session.add(profile)
        
        profile.org_name = data.get('org_name', '')
        profile.org_name_kana = data.get('org_name_kana', '')
        profile.postal_code = data.get('postal_code', '')
        profile.address = data.get('address', '')
        profile.phone = data.get('phone', '')
        profile.email = data.get('email', '')
        profile.representative = data.get('representative', '')
        profile.registration_number = data.get('registration_number', '')
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/dashboard-data')
@login_required
def api_dashboard_data():
    deals_by_stage = db.session.query(
        Deal.stage, db.func.count(Deal.id)
    ).group_by(Deal.stage).all()
    
    deals_by_status = db.session.query(
        Deal.status, db.func.count(Deal.id)
    ).group_by(Deal.status).all()
    
    tasks_by_status = db.session.query(
        Task.status, db.func.count(Task.id)
    ).group_by(Task.status).all()
    
    return jsonify({
        'deals_by_stage': [{'stage': stage, 'count': count} for stage, count in deals_by_stage],
        'deals_by_status': [{'status': status, 'count': count} for status, count in deals_by_status],
        'tasks_by_status': [{'status': status, 'count': count} for status, count in tasks_by_status]
    })

@app.route('/api/dashboard-kpis')
@login_required
def api_dashboard_kpis():
    """Enhanced dashboard KPIs with period filtering"""
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    # Get period parameters
    period = request.args.get('period', 'current_month')
    
    today = date.today()
    
    # Calculate date ranges based on period
    if period == 'current_month':
        current_period_start = date(today.year, today.month, 1)
        current_period_end = today
        last_period_start = current_period_start - relativedelta(months=1)
        last_period_end = current_period_start - relativedelta(days=1)
    elif period == 'last_month':
        current_period_start = date(today.year, today.month, 1) - relativedelta(months=1)
        current_period_end = date(today.year, today.month, 1) - relativedelta(days=1)
        last_period_start = current_period_start - relativedelta(months=1)
        last_period_end = current_period_start - relativedelta(days=1)
    elif period == 'current_year':
        current_period_start = date(today.year, 1, 1)
        current_period_end = today
        last_period_start = date(today.year - 1, 1, 1)
        last_period_end = date(today.year - 1, 12, 31)
    elif period == 'custom':
        # Custom period from query parameters with validation
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            try:
                current_period_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                current_period_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                # Validate start <= end
                if current_period_start > current_period_end:
                    # Swap dates if reversed
                    current_period_start, current_period_end = current_period_end, current_period_start
                
                # For comparison, use the same length period before
                period_length = (current_period_end - current_period_start).days
                last_period_end = current_period_start - relativedelta(days=1)
                last_period_start = last_period_end - relativedelta(days=period_length)
            except ValueError:
                # Invalid date format, fallback to current month
                current_period_start = date(today.year, today.month, 1)
                current_period_end = today
                last_period_start = current_period_start - relativedelta(months=1)
                last_period_end = current_period_start - relativedelta(days=1)
        else:
            # Missing parameters, fallback to current month
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
            last_period_start = current_period_start - relativedelta(months=1)
            last_period_end = current_period_start - relativedelta(days=1)
    else:
        # Default to current month
        current_period_start = date(today.year, today.month, 1)
        current_period_end = today
        last_period_start = current_period_start - relativedelta(months=1)
        last_period_end = current_period_start - relativedelta(days=1)
    
    # Monthly revenue (won deals)
    current_month_revenue = db.session.query(
        db.func.coalesce(db.func.sum(Deal.amount), 0)
    ).filter(
        Deal.status == '受注',
        Deal.created_at >= current_period_start,
        Deal.created_at <= current_period_end
    ).scalar()
    
    last_month_revenue = db.session.query(
        db.func.coalesce(db.func.sum(Deal.amount), 0)
    ).filter(
        Deal.status == '受注',
        Deal.created_at >= last_period_start,
        Deal.created_at <= last_period_end
    ).scalar()
    
    # Pipeline value by stage
    pipeline_by_stage = db.session.query(
        Deal.stage, 
        db.func.sum(Deal.amount).label('total')
    ).filter(
        Deal.status == '進行中'
    ).group_by(Deal.stage).all()
    
    total_pipeline = sum(stage[1] for stage in pipeline_by_stage if stage[1])
    
    # Active deals count
    active_deals = Deal.query.filter_by(status='進行中').count()
    won_deals = Deal.query.filter_by(status='受注').count()
    lost_deals = Deal.query.filter_by(status='失注').count()
    
    # Win rate
    total_closed = won_deals + lost_deals
    win_rate = (won_deals / total_closed * 100) if total_closed > 0 else 0
    
    # Top companies by deal value
    top_companies = db.session.query(
        Company.id,
        Company.name,
        db.func.sum(Deal.amount).label('total_value'),
        db.func.count(Deal.id).label('deal_count')
    ).join(Deal).filter(
        Deal.status == '進行中'
    ).group_by(Company.id, Company.name).order_by(
        db.text('total_value DESC')
    ).limit(5).all()
    
    # Deals with long stage duration (30+ days)
    stale_deals = Deal.query.filter(
        Deal.status == '進行中',
        Deal.stage_entered_at != None
    ).all()
    
    stale_count = sum(1 for deal in stale_deals if deal.days_in_stage and deal.days_in_stage >= 30)
    
    # Activities in selected period
    activities_count = Activity.query.filter(
        Activity.happened_at >= current_period_start,
        Activity.happened_at <= current_period_end
    ).count()
    
    return jsonify({
        'revenue': {
            'current_month': float(current_month_revenue) if current_month_revenue else 0,
            'last_month': float(last_month_revenue) if last_month_revenue else 0,
            'growth_rate': ((current_month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
        },
        'pipeline': {
            'total_value': float(total_pipeline) if total_pipeline else 0,
            'active_deals': active_deals,
            'by_stage': [{'stage': stage, 'value': float(value)} for stage, value in pipeline_by_stage]
        },
        'conversion': {
            'won': won_deals,
            'lost': lost_deals,
            'win_rate': round(win_rate, 1)
        },
        'top_companies': [{
            'id': comp[0],
            'name': comp[1],
            'value': float(comp[2]),
            'deal_count': comp[3]
        } for comp in top_companies],
        'alerts': {
            'stale_deals': stale_count
        },
        'activities': {
            'this_month': activities_count
        }
    })

@app.route('/api/dashboard/revenue-by-assignee')
@login_required
def api_revenue_by_assignee():
    """Get revenue by assignee for a period"""
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    period = request.args.get('period', 'current_month')
    today = date.today()
    
    # Calculate date range
    if period == 'current_month':
        period_start = date(today.year, today.month, 1)
        period_end = today
    elif period == 'last_month':
        first_of_this_month = date(today.year, today.month, 1)
        period_start = first_of_this_month - relativedelta(months=1)
        period_end = first_of_this_month - relativedelta(days=1)
    elif period == 'current_year':
        period_start = date(today.year, 1, 1)
        period_end = today
    else:
        period_start = date(today.year, today.month, 1)
        period_end = today
    
    # Query revenue by assignee
    query = db.session.query(
        User.id,
        User.name,
        db.func.sum(Deal.amount).label('total_revenue'),
        db.func.count(Deal.id).label('deal_count')
    ).join(Deal, Deal.assignee_id == User.id).filter(
        Deal.status == 'WON',
        db.func.date(Deal.closed_at) >= period_start,
        db.func.date(Deal.closed_at) <= period_end
    ).group_by(User.id, User.name).order_by(db.text('total_revenue DESC'))
    
    results = query.all()
    
    return jsonify({
        'period': period,
        'period_start': period_start.isoformat(),
        'period_end': period_end.isoformat(),
        'data': [{
            'user_id': r[0],
            'user_name': r[1],
            'total_revenue': float(r[2]) if r[2] else 0,
            'deal_count': r[3]
        } for r in results]
    })

@app.route('/api/dashboard/revenue-by-month')
@login_required
def api_revenue_by_month():
    """Get revenue by month for a period"""
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    period = request.args.get('period', 'current_year')
    today = date.today()
    
    # Calculate date range
    if period == 'current_year':
        period_start = date(today.year, 1, 1)
        period_end = today
    elif period == 'last_year':
        period_start = date(today.year - 1, 1, 1)
        period_end = date(today.year - 1, 12, 31)
    elif period == 'last_12_months':
        period_start = today - relativedelta(months=11)
        period_start = date(period_start.year, period_start.month, 1)
        period_end = today
    else:
        period_start = date(today.year, 1, 1)
        period_end = today
    
    # Query revenue by month (compatible with both SQLite and PostgreSQL)
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    is_postgres = 'postgresql' in db_url if db_url else False
    
    if is_postgres:
        # PostgreSQL: use to_char
        month_expr = db.func.to_char(Deal.closed_at, 'YYYY-MM')
    else:
        # SQLite: use strftime
        month_expr = db.func.strftime('%Y-%m', Deal.closed_at)
    
    query = db.session.query(
        month_expr.label('month'),
        db.func.sum(Deal.amount).label('total_revenue'),
        db.func.count(Deal.id).label('deal_count')
    ).filter(
        Deal.status == 'WON',
        db.func.date(Deal.closed_at) >= period_start,
        db.func.date(Deal.closed_at) <= period_end
    ).group_by('month').order_by('month')
    
    results = query.all()
    
    return jsonify({
        'period': period,
        'period_start': period_start.isoformat(),
        'period_end': period_end.isoformat(),
        'data': [{
            'month': r[0],
            'total_revenue': float(r[1]) if r[1] else 0,
            'deal_count': r[2]
        } for r in results]
    })

# ============================================================
# Activities API
# ============================================================

@app.route('/activities/export')
@login_required
def export_activities():
    """活動履歴データをCSV/Excelでエクスポート"""
    guard = ensure_import_export_permission('companies')
    if guard:
        return guard
    format_type = request.args.get('format', 'csv')  # csv or excel
    company_id = request.args.get('company_id', '')
    
    query = Activity.query.join(Company).join(User)
    
    # 企業IDでフィルタ（指定されている場合）
    if company_id:
        try:
            query = query.filter(Activity.company_id == int(company_id))
        except ValueError:
            pass
    
    # 日付範囲でフィルタ（オプション）
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(db.func.date(Activity.happened_at) >= from_dt.date())
        except ValueError:
            pass
    
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter(db.func.date(Activity.happened_at) <= to_dt.date())
        except ValueError:
            pass
    
    # 活動タイプでフィルタ（オプション）
    activity_type = request.args.get('type', '')
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    
    activities_list = query.order_by(Activity.happened_at.desc()).all()
    
    # ファイル名に現在の日時を含める
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == 'excel':
        excel_file = export_activities_to_excel(activities_list)
        filename = f'活動履歴_{timestamp}.xlsx'
        if company_id:
            company = Company.query.get(company_id)
            if company:
                filename = f'活動履歴_{company.name}_{timestamp}.xlsx'
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    else:
        csv_data = export_activities_to_csv(activities_list)
        filename = f'活動履歴_{timestamp}.csv'
        if company_id:
            company = Company.query.get(company_id)
            if company:
                filename = f'活動履歴_{company.name}_{timestamp}.csv'
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response

@app.route('/api/companies/<int:company_id>/activities', methods=['GET'])
@login_required
def get_company_activities(company_id):
    """Get activities for a company with pagination"""
    try:
        company = Company.query.get_or_404(company_id)
        
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        activities = Activity.query.filter_by(company_id=company_id)\
            .order_by(Activity.happened_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        total = Activity.query.filter_by(company_id=company_id).count()
        
        return jsonify({
            'success': True,
            'activities': [activity.to_dict() for activity in activities],
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>/activities', methods=['POST'])
@login_required
def create_company_activity(company_id):
    """Create a new activity for a company"""
    try:
        company = Company.query.get_or_404(company_id)
        
        data = request.get_json()
        
        # Validation
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        activity_type = data.get('type')
        title = data.get('title')
        
        if not activity_type or activity_type not in ['call', 'meeting', 'email', 'note']:
            return jsonify({'success': False, 'error': 'Invalid activity type'}), 400
        
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        # Create activity
        activity = Activity(
            company_id=company_id,
            user_id=current_user.id,
            deal_id=data.get('deal_id'),
            type=activity_type,
            title=title,
            body=data.get('body'),
            happened_at=datetime.fromisoformat(data.get('happened_at')) if data.get('happened_at') else datetime.utcnow()
        )
        
        db.session.add(activity)
        
        # Update last_contacted_at for company
        company.last_contacted_at = activity.happened_at
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'activity': activity.to_dict(),
            'message': '活動を記録しました。'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>', methods=['GET'])
@login_required
def get_company_detail(company_id):
    """Get detailed company information"""
    try:
        company = Company.query.get_or_404(company_id)
        
        # Get related data counts
        deals_count = Deal.query.filter_by(company_id=company_id).count()
        contacts_count = Contact.query.filter_by(company_id=company_id).count()
        activities_count = Activity.query.filter_by(company_id=company_id).count()
        
        # Get open deals
        open_deals = Deal.query.filter_by(company_id=company_id, status='進行中').all()
        
        return jsonify({
            'success': True,
            'company': {
                'id': company.id,
                'name': company.name,
                'industry': company.industry,
                'location': company.location,
                'employee_size': company.employee_size,
                'hq_location': company.hq_location,
                'website': company.website,
                'needs': company.needs,
                'kpi_current': company.kpi_current,
                'heat_score': company.heat_score or 1,
                'last_contacted_at': company.last_contacted_at.isoformat() if company.last_contacted_at else None,
                'next_action_at': company.next_action_at.isoformat() if company.next_action_at else None,
                'tags': company.get_tags_list(),
                'memo': company.memo,
                'created_at': company.created_at.isoformat() if company.created_at else None,
                'deals_count': deals_count,
                'contacts_count': contacts_count,
                'activities_count': activities_count
            },
            'open_deals': [{
                'id': deal.id,
                'title': deal.title,
                'stage': deal.stage,
                'amount': deal.amount,
                'status': deal.status,
                'days_in_stage': deal.days_in_stage
            } for deal in open_deals]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>', methods=['PUT'])
@login_required
def update_company_detail(company_id):
    """Update company information"""
    try:
        company = Company.query.get_or_404(company_id)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            company.name = data['name']
        if 'industry' in data:
            company.industry = data['industry']
        if 'location' in data:
            company.location = data['location']
        if 'employee_size' in data:
            company.employee_size = data['employee_size']
        if 'hq_location' in data:
            company.hq_location = data['hq_location']
        if 'website' in data:
            company.website = data['website']
        if 'needs' in data:
            company.needs = data['needs']
        if 'kpi_current' in data:
            company.kpi_current = data['kpi_current']
        if 'heat_score' in data:
            heat_score = int(data['heat_score'])
            if 1 <= heat_score <= 5:
                company.heat_score = heat_score
        if 'next_action_at' in data:
            company.next_action_at = datetime.fromisoformat(data['next_action_at']) if data['next_action_at'] else None
        if 'memo' in data:
            company.memo = data['memo']
        if 'tags' in data:
            company.set_tags_list(data['tags'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '企業情報を更新しました。'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>/contacts', methods=['GET'])
@login_required
def get_company_contacts(company_id):
    """Get all contacts for a specific company"""
    try:
        contacts = Contact.query.filter_by(company_id=company_id).all()
        
        return jsonify({
            'success': True,
            'contacts': [{
                'id': contact.id,
                'name': contact.name,
                'title': contact.title,
                'email': contact.email,
                'phone': contact.phone,
                'role': contact.role,
                'notes': contact.notes
            } for contact in contacts]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>/contacts', methods=['POST'])
@login_required
def create_company_contact(company_id):
    """Create a new contact for a specific company"""
    try:
        company = Company.query.get_or_404(company_id)
        
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        contact = Contact(
            company_id=company_id,
            name=data['name'],
            title=data.get('title'),
            email=data.get('email'),
            phone=data.get('phone'),
            role=data.get('role'),
            notes=data.get('notes')
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '担当者を追加しました。',
            'contact': {
                'id': contact.id,
                'name': contact.name,
                'title': contact.title,
                'email': contact.email,
                'phone': contact.phone,
                'role': contact.role,
                'notes': contact.notes
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
@login_required
def get_contact(contact_id):
    """Get contact details"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        return jsonify({
            'success': True,
            'contact': {
                'id': contact.id,
                'company_id': contact.company_id,
                'name': contact.name,
                'title': contact.title,
                'email': contact.email,
                'phone': contact.phone,
                'role': contact.role,
                'notes': contact.notes
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
@login_required
def update_contact_api(contact_id):
    """Update contact information"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        if 'name' in data:
            contact.name = data['name']
        if 'title' in data:
            contact.title = data['title']
        if 'email' in data:
            contact.email = data['email']
        if 'phone' in data:
            contact.phone = data['phone']
        if 'role' in data:
            contact.role = data['role']
        if 'notes' in data:
            contact.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '担当者情報を更新しました。',
            'contact': {
                'id': contact.id,
                'name': contact.name,
                'title': contact.title,
                'email': contact.email,
                'phone': contact.phone,
                'role': contact.role,
                'notes': contact.notes
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact_api(contact_id):
    """Delete a contact"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        db.session.delete(contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '担当者を削除しました。'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# Win/Loss Reason Tracking APIs (v2.6.0)
# ============================================================================

@app.route('/api/deals/<int:deal_id>/close', methods=['PUT'])
@login_required
def close_deal(deal_id):
    """Close a deal with win/loss reason"""
    try:
        deal = Deal.query.get_or_404(deal_id)
        data = request.get_json()
        
        # Validate required fields
        if 'status' not in data:
            return jsonify({'success': False, 'error': 'ステータスは必須です。'}), 400
        
        status = data['status']
        if status not in ['WON', 'LOST']:
            return jsonify({'success': False, 'error': 'ステータスはWONまたはLOSTである必要があります。'}), 400
        
        # Validate reason category
        reason_category = data.get('reason_category', '').strip()
        reason_detail = data.get('reason_detail', '').strip()
        
        if status == 'WON':
            if reason_category and reason_category not in WIN_REASON_CATEGORIES:
                return jsonify({'success': False, 'error': '無効な受注理由カテゴリです。'}), 400
            
            # Validate "その他" requires detail
            if reason_category == 'その他' and not reason_detail:
                return jsonify({'success': False, 'error': '「その他」を選択した場合、詳細は必須です。'}), 400
            
            # Set win reason fields
            deal.win_reason_category = reason_category if reason_category else None
            deal.win_reason_detail = reason_detail if reason_detail else None
            # Clear loss reason fields
            deal.lost_reason_category = None
            deal.lost_reason_detail = None
        
        elif status == 'LOST':
            if reason_category and reason_category not in LOSS_REASON_CATEGORIES:
                return jsonify({'success': False, 'error': '無効な失注理由カテゴリです。'}), 400
            
            # Validate "その他" requires detail
            if reason_category == 'その他' and not reason_detail:
                return jsonify({'success': False, 'error': '「その他」を選択した場合、詳細は必須です。'}), 400
            
            # Set loss reason fields
            deal.lost_reason_category = reason_category if reason_category else None
            deal.lost_reason_detail = reason_detail if reason_detail else None
            # Clear win reason fields
            deal.win_reason_category = None
            deal.win_reason_detail = None
        
        # Update deal status and closed_at
        deal.status = status
        deal.closed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'案件を{("受注" if status == "WON" else "失注")}としてクローズしました。',
            'deal': {
                'id': deal.id,
                'title': deal.title,
                'status': deal.status,
                'closed_at': deal.closed_at.isoformat() if deal.closed_at else None,
                'win_reason_category': deal.win_reason_category,
                'win_reason_detail': deal.win_reason_detail,
                'lost_reason_category': deal.lost_reason_category,
                'lost_reason_detail': deal.lost_reason_detail
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/win_rate', methods=['GET'])
@login_required
def analytics_win_rate():
    """Get win rate analytics for a period"""
    try:
        # Support both period and from/to parameters
        period = request.args.get('period', 'current_month')
        from_date_str = request.args.get('from') or request.args.get('start_date')
        to_date_str = request.args.get('to') or request.args.get('end_date')
        
        # Calculate date range based on period
        from dateutil.relativedelta import relativedelta
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            # Use explicit dates
            current_period_start = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            current_period_end = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        elif period == 'current_month':
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
        elif period == 'last_month':
            first_of_this_month = date(today.year, today.month, 1)
            current_period_start = first_of_this_month - relativedelta(months=1)
            current_period_end = first_of_this_month - relativedelta(days=1)
        elif period == 'current_year':
            current_period_start = date(today.year, 1, 1)
            current_period_end = today
        else:
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
        
        # Build query
        # Use date comparison to include full day
        query = Deal.query.filter(
            Deal.status.in_(['WON', 'LOST']),
            db.func.date(Deal.closed_at) >= current_period_start,
            db.func.date(Deal.closed_at) <= current_period_end
        )
        
        deals = query.all()
        
        won = sum(1 for d in deals if d.status == 'WON')
        lost = sum(1 for d in deals if d.status == 'LOST')
        total_closed = won + lost
        win_rate = (won / total_closed) if total_closed > 0 else 0
        
        return jsonify({
            'win_rate': round(win_rate, 4),
            'won': won,
            'lost': lost,
            'total_closed': total_closed
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/win_reasons', methods=['GET'])
@login_required
def analytics_win_reasons():
    """Get win reasons distribution"""
    try:
        # Support both period and from/to parameters  
        period = request.args.get('period', 'current_month')
        from_date_str = request.args.get('from') or request.args.get('start_date')
        to_date_str = request.args.get('to') or request.args.get('end_date')
        
        # Calculate date range based on period
        from dateutil.relativedelta import relativedelta
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            current_period_start = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            current_period_end = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        elif period == 'current_month':
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
        elif period == 'last_month':
            first_of_this_month = date(today.year, today.month, 1)
            current_period_start = first_of_this_month - relativedelta(months=1)
            current_period_end = first_of_this_month - relativedelta(days=1)
        elif period == 'current_year':
            current_period_start = date(today.year, 1, 1)
            current_period_end = today
        else:
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
        
        # Build query
        # Use date comparison to include full day
        query = db.session.query(
            Deal.win_reason_category,
            db.func.count(Deal.id).label('count')
        ).filter(
            Deal.status == 'WON',
            Deal.win_reason_category.isnot(None),
            db.func.date(Deal.closed_at) >= current_period_start,
            db.func.date(Deal.closed_at) <= current_period_end
        )
        
        results = query.group_by(Deal.win_reason_category).order_by(db.text('count DESC')).all()
        
        data = [{'category': r[0], 'count': r[1]} for r in results]
        
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/loss_reasons', methods=['GET'])
@login_required
def analytics_loss_reasons():
    """Get loss reasons distribution"""
    try:
        # Support both period and from/to parameters
        period = request.args.get('period', 'current_month')
        from_date_str = request.args.get('from') or request.args.get('start_date')
        to_date_str = request.args.get('to') or request.args.get('end_date')
        
        # Calculate date range based on period
        from dateutil.relativedelta import relativedelta
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            current_period_start = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            current_period_end = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        elif period == 'current_month':
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
        elif period == 'last_month':
            first_of_this_month = date(today.year, today.month, 1)
            current_period_start = first_of_this_month - relativedelta(months=1)
            current_period_end = first_of_this_month - relativedelta(days=1)
        elif period == 'current_year':
            current_period_start = date(today.year, 1, 1)
            current_period_end = today
        else:
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
        
        # Build query
        # Use date comparison to include full day
        query = db.session.query(
            Deal.lost_reason_category,
            db.func.count(Deal.id).label('count')
        ).filter(
            Deal.status == 'LOST',
            Deal.lost_reason_category.isnot(None),
            db.func.date(Deal.closed_at) >= current_period_start,
            db.func.date(Deal.closed_at) <= current_period_end
        )
        
        results = query.group_by(Deal.lost_reason_category).order_by(db.text('count DESC')).all()
        
        data = [{'category': r[0], 'count': r[1]} for r in results]
        
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/reasons_top5', methods=['GET'])
@login_required
def analytics_reasons_top5():
    """Get top 5 win and loss reasons"""
    try:
        # Support both period and from/to parameters
        period = request.args.get('period', 'current_month')
        from_date_str = request.args.get('from') or request.args.get('start_date')
        to_date_str = request.args.get('to') or request.args.get('end_date')
        
        # Calculate date range based on period
        from dateutil.relativedelta import relativedelta
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            current_period_start = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            current_period_end = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        elif period == 'current_month':
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
        elif period == 'last_month':
            first_of_this_month = date(today.year, today.month, 1)
            current_period_start = first_of_this_month - relativedelta(months=1)
            current_period_end = first_of_this_month - relativedelta(days=1)
        elif period == 'current_year':
            current_period_start = date(today.year, 1, 1)
            current_period_end = today
        else:
            current_period_start = date(today.year, today.month, 1)
            current_period_end = today
        
        # Win reasons top 5
        win_query = db.session.query(
            Deal.win_reason_category,
            db.func.count(Deal.id).label('count')
        ).filter(
            Deal.status == 'WON',
            Deal.win_reason_category.isnot(None),
            Deal.closed_at >= current_period_start,
            Deal.closed_at <= current_period_end
        )
        
        win_results = win_query.group_by(Deal.win_reason_category).order_by(db.text('count DESC')).limit(5).all()
        
        # Loss reasons top 5
        loss_query = db.session.query(
            Deal.lost_reason_category,
            db.func.count(Deal.id).label('count')
        ).filter(
            Deal.status == 'LOST',
            Deal.lost_reason_category.isnot(None),
            Deal.closed_at >= current_period_start,
            Deal.closed_at <= current_period_end
        )
        
        loss_results = loss_query.group_by(Deal.lost_reason_category).order_by(db.text('count DESC')).limit(5).all()
        
        return jsonify({
            'win_reasons': [{'category': r[0], 'count': r[1]} for r in win_results],
            'loss_reasons': [{'category': r[0], 'count': r[1]} for r in loss_results]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# INDUSTRY ANALYTICS ENDPOINTS
# ============================================

@app.route('/api/analytics/industry/win_rate_ranking', methods=['GET'])
@login_required
def industry_win_rate_ranking():
    """Get win rate ranking by industry"""
    try:
        # Support both period and from/to parameters
        period = request.args.get('period', 'current_month')
        from_date_str = request.args.get('from')
        to_date_str = request.args.get('to')
        
        # Calculate date range
        from dateutil.relativedelta import relativedelta
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        elif period == 'current_month':
            from_date = date(today.year, today.month, 1)
            to_date = today
        elif period == 'current_quarter':
            quarter_month = ((today.month - 1) // 3) * 3 + 1
            from_date = date(today.year, quarter_month, 1)
            to_date = today
        elif period == 'current_year':
            from_date = date(today.year, 1, 1)
            to_date = today
        else:
            from_date = date(today.year, today.month, 1)
            to_date = today
        
        # Query deals with companies, filter by closed date and status
        query = db.session.query(
            Company.industry,
            db.func.sum(db.case((Deal.status == 'WON', 1), else_=0)).label('won'),
            db.func.sum(db.case((Deal.status == 'LOST', 1), else_=0)).label('lost')
        ).join(Deal, Deal.company_id == Company.id).filter(
            Deal.status.in_(['WON', 'LOST']),
            Company.industry.isnot(None),
            db.func.date(Deal.closed_at) >= from_date,
            db.func.date(Deal.closed_at) <= to_date
        ).group_by(Company.industry)
        
        results = query.all()
        
        # Calculate win rate and format data
        data = []
        for r in results:
            industry = r[0]
            won = r[1] or 0
            lost = r[2] or 0
            total = won + lost
            win_rate = (won / total) if total > 0 else 0
            
            data.append({
                'industry': industry,
                'win_rate': round(win_rate, 4),
                'won': won,
                'lost': lost
            })
        
        # Sort by win_rate descending
        data.sort(key=lambda x: x['win_rate'], reverse=True)
        
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/industry/avg_amount', methods=['GET'])
@login_required
def industry_avg_amount():
    """Get average deal amount for a specific industry"""
    try:
        industry = request.args.get('industry')
        from_date_str = request.args.get('from')
        to_date_str = request.args.get('to')
        
        # Calculate date range
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        else:
            from_date = date(today.year, today.month, 1)
            to_date = today
        
        # Build query
        query = db.session.query(
            db.func.avg(Deal.amount).label('avg_amount'),
            db.func.count(Deal.id).label('count')
        ).join(Company, Deal.company_id == Company.id).filter(
            Deal.status == 'WON',
            db.func.date(Deal.closed_at) >= from_date,
            db.func.date(Deal.closed_at) <= to_date
        )
        
        # Add industry filter if specified
        if industry:
            query = query.filter(Company.industry == industry)
        
        result = query.first()
        
        avg_amount = float(result[0]) if result[0] else 0
        count = result[1] or 0
        
        return jsonify({
            'industry': industry or 'すべて',
            'avg_amount': round(avg_amount, 2),
            'count': count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/industry/win_rate', methods=['GET'])
@login_required
def industry_win_rate():
    """Get win rate for a specific industry"""
    try:
        industry = request.args.get('industry')
        from_date_str = request.args.get('from')
        to_date_str = request.args.get('to')
        
        # Calculate date range
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        else:
            from_date = date(today.year, today.month, 1)
            to_date = today
        
        # Build query
        query = db.session.query(
            db.func.sum(db.case((Deal.status == 'WON', 1), else_=0)).label('won'),
            db.func.sum(db.case((Deal.status == 'LOST', 1), else_=0)).label('lost')
        ).join(Company, Deal.company_id == Company.id).filter(
            Deal.status.in_(['WON', 'LOST']),
            db.func.date(Deal.closed_at) >= from_date,
            db.func.date(Deal.closed_at) <= to_date
        )
        
        # Add industry filter if specified
        if industry:
            query = query.filter(Company.industry == industry)
        
        result = query.first()
        
        won = result[0] or 0
        lost = result[1] or 0
        total = won + lost
        win_rate = (won / total) if total > 0 else 0
        
        return jsonify({
            'industry': industry or 'すべて',
            'win_rate': round(win_rate, 4),
            'won': won,
            'lost': lost
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/industry/win_reasons', methods=['GET'])
@login_required
def industry_win_reasons():
    """Get win reasons distribution for a specific industry"""
    try:
        industry = request.args.get('industry')
        from_date_str = request.args.get('from')
        to_date_str = request.args.get('to')
        
        # Calculate date range
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        else:
            from_date = date(today.year, today.month, 1)
            to_date = today
        
        # Build query
        query = db.session.query(
            Deal.win_reason_category,
            db.func.count(Deal.id).label('count')
        ).join(Company, Deal.company_id == Company.id).filter(
            Deal.status == 'WON',
            Deal.win_reason_category.isnot(None),
            db.func.date(Deal.closed_at) >= from_date,
            db.func.date(Deal.closed_at) <= to_date
        )
        
        # Add industry filter if specified
        if industry:
            query = query.filter(Company.industry == industry)
        
        results = query.group_by(Deal.win_reason_category).order_by(db.text('count DESC')).all()
        
        data = [{'category': r[0], 'count': r[1]} for r in results]
        
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/industry/loss_reasons', methods=['GET'])
@login_required
def industry_loss_reasons():
    """Get loss reasons distribution for a specific industry"""
    try:
        industry = request.args.get('industry')
        from_date_str = request.args.get('from')
        to_date_str = request.args.get('to')
        
        # Calculate date range
        from datetime import date
        today = date.today()
        
        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        else:
            from_date = date(today.year, today.month, 1)
            to_date = today
        
        # Build query
        query = db.session.query(
            Deal.lost_reason_category,
            db.func.count(Deal.id).label('count')
        ).join(Company, Deal.company_id == Company.id).filter(
            Deal.status == 'LOST',
            Deal.lost_reason_category.isnot(None),
            db.func.date(Deal.closed_at) >= from_date,
            db.func.date(Deal.closed_at) <= to_date
        )
        
        # Add industry filter if specified
        if industry:
            query = query.filter(Company.industry == industry)
        
        results = query.group_by(Deal.lost_reason_category).order_by(db.text('count DESC')).all()
        
        data = [{'category': r[0], 'count': r[1]} for r in results]
        
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# QUOTE MANAGEMENT ENDPOINTS
# ============================================

@app.route('/quotes')
@login_required
def quotes():
    """Quote list page"""
    quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    return render_template('quotes.html', quotes=quotes)

@app.route('/quotes/new')
@login_required
def new_quote():
    """New quote form"""
    companies = Company.query.order_by(Company.name).all()
    return render_template('quote_form.html', companies=companies)

@app.route('/quotes/<int:id>')
@login_required
def view_quote(id):
    """Quote detail page"""
    quote = db.session.get(Quote, id)
    if not quote:
        flash('見積が見つかりませんでした', 'error')
        return redirect(url_for('quotes'))
    return render_template('quote_detail.html', quote=quote)

@app.route('/quotes/<int:id>/edit')
@login_required
def edit_quote(id):
    """Edit quote form"""
    quote = db.session.get(Quote, id)
    if not quote:
        flash('見積が見つかりませんでした', 'error')
        return redirect(url_for('quotes'))
    companies = Company.query.order_by(Company.name).all()
    return render_template('quote_form.html', quote=quote, companies=companies)

@app.route('/api/quotes', methods=['POST'])
@login_required
def create_quote():
    """Create a new quote"""
    try:
        data = request.get_json()
        quote = Quote(
            company_id=data['company_id'],
            contact_id=data.get('contact_id'),
            issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d').date(),
            expire_date=datetime.strptime(data['expire_date'], '%Y-%m-%d').date() if data.get('expire_date') else None,
            subject=data['subject'],
            tax_rate=float(data.get('tax_rate', 0.10)),
            notes=data.get('notes', ''),
            status='下書き'
        )
        db.session.add(quote)
        db.session.flush()
        
        for item_data in data.get('items', []):
            item = QuoteItem(
                quote_id=quote.id,
                item_name=item_data['item_name'],
                description=item_data.get('description', ''),
                qty=float(item_data.get('qty', 1)),
                unit_price=float(item_data.get('unit_price', 0)),
                tax_rate=float(item_data.get('tax_rate', 0.10))
            )
            item.calculate_line_total()
            db.session.add(item)
        
        quote.calculate_totals()
        db.session.commit()
        
        return jsonify({'success': True, 'id': quote.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/quotes/<int:id>', methods=['PUT'])
@login_required
def update_quote(id):
    """Update a quote"""
    try:
        quote = db.session.get(Quote, id)
        if not quote:
            return jsonify({'success': False, 'error': '見積が見つかりません'}), 404
        
        data = request.get_json()
        quote.company_id = data.get('company_id', quote.company_id)
        quote.contact_id = data.get('contact_id')
        quote.issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d').date() if 'issue_date' in data else quote.issue_date
        quote.expire_date = datetime.strptime(data['expire_date'], '%Y-%m-%d').date() if data.get('expire_date') else None
        quote.subject = data.get('subject', quote.subject)
        quote.tax_rate = float(data.get('tax_rate', quote.tax_rate))
        quote.notes = data.get('notes', quote.notes)
        
        if 'items' in data:
            for item in quote.items:
                db.session.delete(item)
            
            for item_data in data['items']:
                item = QuoteItem(
                    quote_id=quote.id,
                    item_name=item_data['item_name'],
                    description=item_data.get('description', ''),
                    qty=float(item_data.get('qty', 1)),
                    unit_price=float(item_data.get('unit_price', 0)),
                    tax_rate=float(item_data.get('tax_rate', 0.10))
                )
                item.calculate_line_total()
                db.session.add(item)
            
            quote.calculate_totals()
        
        db.session.commit()
        return jsonify({'success': True, 'id': quote.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/quotes/<int:id>/issue', methods=['POST'])
@login_required
def issue_quote(id):
    """Issue a quote (assign number and change status)"""
    try:
        quote = db.session.get(Quote, id)
        if not quote:
            return jsonify({'success': False, 'error': '見積が見つかりません'}), 404
        
        if quote.status != '下書き':
            return jsonify({'success': False, 'error': 'この見積はすでに発行されています'}), 400
        
        from utils.numbering import generate_quote_number
        quote.quote_no = generate_quote_number()
        quote.status = '発行済み'
        quote.calculate_totals()
        
        db.session.commit()
        return jsonify({'success': True, 'quote_no': quote.quote_no})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/quotes/<int:id>/pdf', methods=['GET'])
@login_required
def download_quote_pdf(id):
    """Generate and download quote PDF"""
    try:
        from utils.pdf_generator import generate_quote_pdf
        from flask import send_file
        import io
        
        pdf_bytes = generate_quote_pdf(id)
        quote = db.session.get(Quote, id)
        filename = f'quote_{quote.quote_no or id}.pdf'
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/deals/<int:deal_id>/create-quote', methods=['POST'])
@login_required
def create_quote_from_deal(deal_id):
    """Create a new quote from a deal"""
    try:
        deal = Deal.query.get_or_404(deal_id)
        
        # Validate deal amount
        if not deal.amount or deal.amount <= 0:
            return jsonify({'success': False, 'error': '案件金額が設定されていません'}), 400
        
        # Create quote with deal information
        today = datetime.now().date()
        expire_date = today + timedelta(days=30)  # Default 30 days expiration
        
        quote = Quote(
            company_id=deal.company_id,
            deal_id=deal.id,
            issue_date=today,
            expire_date=expire_date,
            subject=deal.title,
            tax_rate=0.10,
            notes=f'案件「{deal.title}」より作成',
            status='発行済み'
        )
        db.session.add(quote)
        db.session.flush()
        
        # Create single item from deal
        item = QuoteItem(
            quote_id=quote.id,
            item_name=deal.title,
            description='',
            qty=1,
            unit_price=deal.amount,
            tax_rate=0.10
        )
        item.calculate_line_total()
        db.session.add(item)
        
        quote.calculate_totals()
        db.session.commit()
        
        return jsonify({'success': True, 'id': quote.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/quotes/<int:id>/status', methods=['POST'])
@login_required
def update_quote_status(id):
    """Update quote status"""
    try:
        quote = Quote.query.get_or_404(id)
        data = request.get_json()
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['発行済み', '受注', '失注']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'error': '無効なステータスです'}), 400
        
        quote.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'status': new_status})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================
# INVOICE MANAGEMENT ENDPOINTS
# ============================================

@app.route('/invoices')
@login_required
def invoices():
    """Invoice list page"""
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('invoices.html', invoices=invoices)

@app.route('/invoices/new')
@login_required
def new_invoice():
    """New invoice form"""
    companies = Company.query.order_by(Company.name).all()
    return render_template('invoice_form.html', companies=companies)

@app.route('/invoices/<int:id>')
@login_required
def view_invoice(id):
    """Invoice detail page"""
    invoice = db.session.get(Invoice, id)
    if not invoice:
        flash('請求が見つかりませんでした', 'error')
        return redirect(url_for('invoices'))
    return render_template('invoice_detail.html', invoice=invoice)

@app.route('/invoices/<int:id>/edit')
@login_required
def edit_invoice(id):
    """Edit invoice form"""
    invoice = db.session.get(Invoice, id)
    if not invoice:
        flash('請求が見つかりませんでした', 'error')
        return redirect(url_for('invoices'))
    companies = Company.query.order_by(Company.name).all()
    return render_template('invoice_form.html', invoice=invoice, companies=companies)

@app.route('/api/invoices', methods=['POST'])
@login_required
def create_invoice():
    """Create a new invoice"""
    try:
        data = request.get_json()
        invoice = Invoice(
            company_id=data['company_id'],
            contact_id=data.get('contact_id'),
            issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d').date(),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            subject=data['subject'],
            person_in_charge=data.get('person_in_charge'),
            tax_rate=float(data.get('tax_rate', 0.10)),
            notes=data.get('notes', ''),
            status='下書き'
        )
        db.session.add(invoice)
        db.session.flush()
        
        for item_data in data.get('items', []):
            item = InvoiceItem(
                invoice_id=invoice.id,
                item_name=item_data['item_name'],
                description=item_data.get('description', ''),
                qty=float(item_data.get('qty', 1)),
                unit_price=float(item_data.get('unit_price', 0)),
                tax_rate=float(item_data.get('tax_rate', 0.10))
            )
            item.calculate_line_total()
            db.session.add(item)
        
        invoice.calculate_totals()
        db.session.commit()
        
        return jsonify({'success': True, 'id': invoice.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/invoices/<int:id>', methods=['PUT'])
@login_required
def update_invoice(id):
    """Update an invoice"""
    try:
        invoice = db.session.get(Invoice, id)
        if not invoice:
            return jsonify({'success': False, 'error': '請求が見つかりません'}), 404
        
        data = request.get_json()
        invoice.company_id = data.get('company_id', invoice.company_id)
        invoice.contact_id = data.get('contact_id')
        invoice.issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d').date() if 'issue_date' in data else invoice.issue_date
        invoice.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None
        invoice.subject = data.get('subject', invoice.subject)
        invoice.person_in_charge = data.get('person_in_charge', invoice.person_in_charge)
        invoice.tax_rate = float(data.get('tax_rate', invoice.tax_rate))
        invoice.notes = data.get('notes', invoice.notes)
        
        if 'items' in data:
            for item in invoice.items:
                db.session.delete(item)
            
            for item_data in data['items']:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    item_name=item_data['item_name'],
                    description=item_data.get('description', ''),
                    qty=float(item_data.get('qty', 1)),
                    unit_price=float(item_data.get('unit_price', 0)),
                    tax_rate=float(item_data.get('tax_rate', 0.10))
                )
                item.calculate_line_total()
                db.session.add(item)
            
            invoice.calculate_totals()
        
        db.session.commit()
        return jsonify({'success': True, 'id': invoice.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/invoices/<int:id>/issue', methods=['POST'])
@login_required
def issue_invoice(id):
    """Issue an invoice (assign number and change status)"""
    try:
        invoice = db.session.get(Invoice, id)
        if not invoice:
            return jsonify({'success': False, 'error': '請求が見つかりません'}), 404
        
        if invoice.status != '下書き':
            return jsonify({'success': False, 'error': 'この請求はすでに発行されています'}), 400
        
        from utils.numbering import generate_invoice_number
        invoice.invoice_no = generate_invoice_number()
        invoice.status = '発行済み'
        invoice.calculate_totals()
        
        db.session.commit()
        return jsonify({'success': True, 'invoice_no': invoice.invoice_no})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/invoices/<int:id>/pdf', methods=['GET'])
@login_required
def download_invoice_pdf(id):
    """Generate and download invoice PDF"""
    try:
        from utils.pdf_generator import generate_invoice_pdf
        from flask import send_file
        import io
        
        pdf_bytes = generate_invoice_pdf(id)
        invoice = db.session.get(Invoice, id)
        filename = f'invoice_{invoice.invoice_no or id}.pdf'
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/deals/<int:deal_id>/create-invoice', methods=['POST'])
@login_required
def create_invoice_from_deal(deal_id):
    """Create a new invoice from a deal"""
    try:
        deal = Deal.query.get_or_404(deal_id)
        
        # Validate deal amount
        if not deal.amount or deal.amount <= 0:
            return jsonify({'success': False, 'error': '案件金額が設定されていません'}), 400
        
        # Create invoice with deal information
        today = datetime.now().date()
        due_date = today + timedelta(days=30)  # Default 30 days payment term
        
        invoice = Invoice(
            company_id=deal.company_id,
            deal_id=deal.id,
            issue_date=today,
            due_date=due_date,
            subject=deal.title,
            tax_rate=0.10,
            notes=f'案件「{deal.title}」より作成',
            status='発行済み'
        )
        db.session.add(invoice)
        db.session.flush()
        
        # Create single item from deal
        item = InvoiceItem(
            invoice_id=invoice.id,
            item_name=deal.title,
            description='',
            qty=1,
            unit_price=deal.amount,
            tax_rate=0.10
        )
        item.calculate_line_total()
        db.session.add(item)
        
        invoice.calculate_totals()
        db.session.commit()
        
        return jsonify({'success': True, 'id': invoice.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/invoices/<int:id>/status', methods=['POST'])
@login_required
def update_invoice_status(id):
    """Update invoice status"""
    try:
        invoice = Invoice.query.get_or_404(id)
        data = request.get_json()
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['発行済み', '入金確認']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'error': '無効なステータスです'}), 400
        
        invoice.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'status': new_status})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# Backup Management Routes
@app.route('/api/backup/create', methods=['POST'])
@login_required
@role_required('admin')
def create_backup_manual():
    """Create manual backup (admin only)"""
    try:
        from utils.backup import create_backup
        backup_path = create_backup()
        log_security_event('backup_created', f'Admin {current_user.email} created manual backup', current_user.id, ip_address=get_client_ip(), user_agent=get_user_agent())
        return jsonify({'success': True, 'backup_path': backup_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/backup/list', methods=['GET'])
@login_required
@role_required('admin')
def list_backups_api():
    """List all backups (admin only)"""
    try:
        from utils.backup import list_backups
        backups = list_backups()
        return jsonify({'success': True, 'backups': backups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Start backup scheduler if enabled
    if os.environ.get('ENABLE_BACKUP_SCHEDULER', 'False').lower() == 'true':
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            from utils.backup import create_backup, cleanup_old_backups
            
            scheduler = BackgroundScheduler()
            scheduler.add_job(
                lambda: create_backup() or cleanup_old_backups(keep_days=30),
                trigger=CronTrigger(hour=2, minute=0),
                id='daily_backup',
                name='Daily database backup',
                replace_existing=True
            )
            scheduler.start()
            print("✓ Backup scheduler started (daily at 2:00 AM)")
        except Exception as e:
            print(f"✗ Failed to start backup scheduler: {e}")
    
    # Replit環境対応：ホストは0.0.0.0、ポート5000を使用
    # 本番環境では環境変数PORTを使用し、debug=Falseに設定
    port = 5000
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
