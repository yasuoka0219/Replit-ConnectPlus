"""
Password reset migration script
Adds password reset token table for password reset functionality
"""
import os
from dotenv import load_dotenv
from flask import Flask
from database import db
from models import PasswordResetToken

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

print("=" * 60)
print("CONNECT+ Password Reset Migration")
print("=" * 60)

with app.app_context():
    print("\n✓ Database connection established")
    print("\nUpdating database schema...")
    print("-" * 60)
    
    try:
        # Create PasswordResetToken table
        print("Creating PasswordResetToken table...")
        db.create_all()
        
        print("\n✓ Password reset table created")
        print("=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        print("\nNew features available:")
        print("  - Password reset via email (メールでパスワード再設定)")
        print("  - Secure token-based password reset")
        print("  - 24-hour token expiration")
        print("\nYou can now:")
        print("  - Click 'パスワードを忘れた場合' on login page")
        print("  - Request password reset via email")
        print("  - Reset password using secure link")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

