"""
Security utility functions for CONNECT+ CRM
Includes password policy, 2FA, login attempt tracking, and security logging
"""
import re
import json
import pyotp
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
from flask import request, session
from models import User, LoginAttempt, SecurityLog, db


# Password policy constants
MIN_PASSWORD_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True

# Login attempt constants
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 30
LOGIN_ATTEMPT_WINDOW_MINUTES = 15


def validate_password_strength(password):
    """
    Validate password against policy
    
    Returns:
        tuple: (is_valid, errors)
        is_valid (bool): True if password meets all requirements
        errors (list): List of error messages
    """
    errors = []
    
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f'パスワードは{MIN_PASSWORD_LENGTH}文字以上である必要があります。')
    
    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append('パスワードには大文字が含まれている必要があります。')
    
    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append('パスワードには小文字が含まれている必要があります。')
    
    if PASSWORD_REQUIRE_DIGIT and not re.search(r'[0-9]', password):
        errors.append('パスワードには数字が含まれている必要があります。')
    
    if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>/?]', password):
        errors.append('パスワードには特殊文字が含まれている必要があります。')
    
    return len(errors) == 0, errors


def log_login_attempt(email, success, user_id=None, ip_address=None, user_agent=None):
    """
    Log login attempt to database
    
    Args:
        email (str): Email address used for login
        success (bool): Whether login was successful
        user_id (int, optional): User ID if successful
        ip_address (str, optional): IP address
        user_agent (str, optional): User agent string
    """
    try:
        attempt = LoginAttempt(
            email=email,
            success=success,
            user_id=user_id,
            ip_address=ip_address or request.remote_addr if request else None,
            user_agent=user_agent or request.headers.get('User-Agent') if request else None
        )
        db.session.add(attempt)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging login attempt: {e}")


def check_login_attempts(email):
    """
    Check if email has too many failed login attempts
    
    Returns:
        tuple: (is_locked, attempts_remaining)
        is_locked (bool): True if account is locked
        attempts_remaining (int): Number of attempts remaining before lockout
    """
    window_start = datetime.utcnow() - timedelta(minutes=LOGIN_ATTEMPT_WINDOW_MINUTES)
    
    recent_attempts = LoginAttempt.query.filter(
        LoginAttempt.email == email,
        LoginAttempt.attempted_at >= window_start,
        LoginAttempt.success == False
    ).count()
    
    attempts_remaining = max(0, MAX_LOGIN_ATTEMPTS - recent_attempts)
    is_locked = recent_attempts >= MAX_LOGIN_ATTEMPTS
    
    return is_locked, attempts_remaining


def log_security_event(event_type, event_description, user_id=None, resource_type=None, resource_id=None, ip_address=None, user_agent=None):
    """
    Log security event to audit log
    
    Args:
        event_type (str): Type of event (login, logout, password_change, 2fa_enabled, etc.)
        event_description (str): Description of the event
        user_id (int, optional): User ID
        resource_type (str, optional): Type of resource affected
        resource_id (int, optional): ID of resource affected
        ip_address (str, optional): IP address
        user_agent (str, optional): User agent string
    """
    try:
        log = SecurityLog(
            user_id=user_id,
            event_type=event_type,
            event_description=event_description,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address or (request.remote_addr if request else None),
            user_agent=user_agent or (request.headers.get('User-Agent') if request else None)
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging security event: {e}")


def generate_2fa_secret(user):
    """
    Generate 2FA secret for user
    
    Args:
        user (User): User object
        
    Returns:
        str: TOTP secret key
    """
    secret = pyotp.random_base32()
    user.two_factor_secret = secret
    db.session.commit()
    return secret


def get_2fa_provisioning_uri(user, secret=None):
    """
    Get provisioning URI for QR code generation
    
    Args:
        user (User): User object
        secret (str, optional): Secret key (uses user's secret if not provided)
        
    Returns:
        str: Provisioning URI
    """
    if not secret:
        secret = user.two_factor_secret
    
    if not secret:
        return None
    
    totp = pyotp.TOTP(secret)
    issuer_name = "CONNECT+ CRM"
    return totp.provisioning_uri(
        name=user.email,
        issuer_name=issuer_name
    )


def generate_2fa_qr_code(provisioning_uri):
    """
    Generate QR code image as base64 string
    
    Args:
        provisioning_uri (str): TOTP provisioning URI
        
    Returns:
        str: Base64 encoded QR code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def verify_2fa_code(user, code, allow_setup=False):
    """
    Verify 2FA code
    
    Args:
        user (User): User object
        code (str): 6-digit code from authenticator app
        allow_setup (bool): If True, allow verification even if 2FA is not enabled yet (for setup)
        
    Returns:
        bool: True if code is valid
    """
    if not user.two_factor_secret:
        return False
    
    # During setup, we allow verification even if 2FA is not enabled yet
    if not allow_setup and not user.two_factor_enabled:
        return False
    
    totp = pyotp.TOTP(user.two_factor_secret)
    
    # Verify current code and previous/next window (for clock skew)
    if totp.verify(code, valid_window=1):
        return True
    
    # Check backup codes (only if 2FA is enabled)
    if allow_setup or user.two_factor_enabled:
        if user.two_factor_backup_codes:
            try:
                backup_codes = json.loads(user.two_factor_backup_codes)
                if code in backup_codes:
                    # Remove used backup code
                    backup_codes.remove(code)
                    user.two_factor_backup_codes = json.dumps(backup_codes) if backup_codes else None
                    db.session.commit()
                    return True
            except (json.JSONDecodeError, ValueError):
                pass
    
    return False


def generate_backup_codes(count=10):
    """
    Generate backup codes for 2FA
    
    Args:
        count (int): Number of codes to generate
        
    Returns:
        list: List of backup codes
    """
    import secrets
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric code
        code = ''.join(secrets.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(8))
        codes.append(code)
    return codes


def get_client_ip():
    """Get client IP address from request"""
    if request:
        # Check for forwarded headers (behind proxy)
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        return request.remote_addr
    return None


def get_user_agent():
    """Get user agent from request"""
    if request:
        return request.headers.get('User-Agent')
    return None

