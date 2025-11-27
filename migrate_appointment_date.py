#!/usr/bin/env python3
"""
Migration script to add appointment_date column to deals table
"""
from database import db
from app import app
from sqlalchemy import text

def migrate():
    """Add appointment_date column to deals table"""
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='deals' AND column_name='appointment_date'
            """))
            
            if result.fetchone():
                print("✓ appointment_date column already exists")
                return
            
            # Add appointment_date column
            print("Adding appointment_date column to deals table...")
            db.session.execute(text("""
                ALTER TABLE deals 
                ADD COLUMN appointment_date DATE
            """))
            
            # Add index for better query performance
            print("Creating index on appointment_date...")
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_deals_appointment_date 
                ON deals(appointment_date)
            """))
            
            db.session.commit()
            print("✓ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("Starting migration: Add appointment_date to deals")
    migrate()
    print("Migration finished!")
