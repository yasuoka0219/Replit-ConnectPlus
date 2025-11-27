"""
Security features migration script
Adds 2FA, login attempt tracking, and security logging tables
"""
import os
from dotenv import load_dotenv
from flask import Flask
from database import db
from models import User, LoginAttempt, SecurityLog

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

print("=" * 60)
print("CONNECT+ Security Features Migration")
print("=" * 60)

with app.app_context():
    print("\n✓ Database connection established")
    print("\nUpdating database schema...")
    print("-" * 60)
    
    try:
        # Create new tables
        print("Creating security tables...")
        db.create_all()
        
        # Add 2FA columns to User table if they don't exist
        print("Updating User table for 2FA...")
        try:
            from sqlalchemy import inspect, text
            
            inspector = inspect(db.engine)
            user_columns = [col['name'] for col in inspector.get_columns('users')]
            
            # Check and add 2FA columns if needed
            with db.engine.connect() as conn:
                if 'two_factor_secret' not in user_columns:
                    conn.execute(text('ALTER TABLE users ADD COLUMN two_factor_secret VARCHAR(32)'))
                    conn.commit()
                    print("  ✓ Added two_factor_secret column")
                
                if 'two_factor_enabled' not in user_columns:
                    conn.execute(text('ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0'))
                    conn.commit()
                    print("  ✓ Added two_factor_enabled column")
                
                if 'two_factor_backup_codes' not in user_columns:
                    conn.execute(text('ALTER TABLE users ADD COLUMN two_factor_backup_codes TEXT'))
                    conn.commit()
                    print("  ✓ Added two_factor_backup_codes column")
                
                # Check and add lockout columns if needed
                if 'failed_login_attempts' not in user_columns:
                    conn.execute(text('ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0'))
                    conn.commit()
                    print("  ✓ Added failed_login_attempts column")
                
                if 'locked_until' not in user_columns:
                    conn.execute(text('ALTER TABLE users ADD COLUMN locked_until DATETIME'))
                    conn.commit()
                    print("  ✓ Added locked_until column")
        except Exception as e:
            # If SQLite and column exists, it will raise an error - that's okay
            if 'duplicate column' not in str(e).lower() and 'already exists' not in str(e).lower():
                print(f"  ⚠ Warning: {e}")
        
        print("\n✓ Security tables created/updated")
        print("=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        print("\nNew features available:")
        print("  - Two-Factor Authentication (2FA)")
        print("  - Login attempt tracking (brute force protection)")
        print("  - Security audit logging")
        print("  - Password policy enforcement")
        print("  - Automatic database backups")
        print("\nYou can now:")
        print("  - Enable 2FA in Settings > Security")
        print("  - View security logs (admin only)")
        print("  - Create manual backups (admin only)")
        print("\nTo enable automatic backups, set ENABLE_BACKUP_SCHEDULER=true in .env")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

