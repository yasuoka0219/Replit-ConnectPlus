"""
Email-based 2FA migration script
Adds email 2FA support to existing 2FA system
"""
import os
from dotenv import load_dotenv
from flask import Flask
from database import db
from models import User, Email2FACode

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

print("=" * 60)
print("CONNECT+ Email-based 2FA Migration")
print("=" * 60)

with app.app_context():
    print("\n✓ Database connection established")
    print("\nUpdating database schema...")
    print("-" * 60)
    
    try:
        # Create Email2FACode table
        print("Creating Email2FACode table...")
        db.create_all()
        
        # Add two_factor_type column to User table if it doesn't exist
        print("Updating User table for email 2FA...")
        try:
            from sqlalchemy import inspect, text
            
            inspector = inspect(db.engine)
            user_columns = [col['name'] for col in inspector.get_columns('users')]
            
            # Check and add two_factor_type column if needed
            with db.engine.connect() as conn:
                if 'two_factor_type' not in user_columns:
                    conn.execute(text('ALTER TABLE users ADD COLUMN two_factor_type VARCHAR(20) DEFAULT "app"'))
                    conn.commit()
                    print("  ✓ Added two_factor_type column")
                
                # Update existing users with 2FA enabled to have type 'app'
                if user_columns.count('two_factor_type') > 0:  # Column exists now
                    conn.execute(text('UPDATE users SET two_factor_type = "app" WHERE two_factor_enabled = 1 AND (two_factor_type IS NULL OR two_factor_type = "")'))
                    conn.commit()
                    print("  ✓ Updated existing 2FA users")
        except Exception as e:
            # If SQLite and column exists, it will raise an error - that's okay
            if 'duplicate column' not in str(e).lower() and 'already exists' not in str(e).lower():
                print(f"  ⚠ Warning: {e}")
        
        print("\n✓ Email 2FA tables created/updated")
        print("=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        print("\nNew features available:")
        print("  - Email-based 2FA (メール認証)")
        print("  - App-based 2FA (認証アプリ)")
        print("  - Choice between QR code or email verification")
        print("\nYou can now:")
        print("  - Select email authentication in Settings > 2FA")
        print("  - Receive verification codes via email")
        print("  - Login with email verification codes")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise





