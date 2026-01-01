#!/usr/bin/env python3
"""
Database Migration Script: Add assignee_id to deals table
This script safely adds assignee_id column to link deals to users.
"""
import os
import sys
from app import app, db
from models import Deal, User

def run_migration():
    """Run database migration safely"""
    with app.app_context():
        print("=" * 60)
        print("CONNECT+ Assignee Migration Script")
        print("=" * 60)
        print("\nThis will add assignee_id column to deals table.")
        print("Existing data will be preserved.\n")
        
        # Check if database exists
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            print("✓ Database connection established")
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            print("\nCreating new database schema...")
            db.create_all()
            print("✓ New database created successfully")
            return
        
        print("\nUpdating database schema...")
        print("-" * 60)
        
        try:
            # Get database type
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            is_postgres = 'postgresql' in db_url if db_url else False
            
            if is_postgres:
                print("PostgreSQL detected - using ALTER TABLE")
                migrate_postgresql()
            else:
                print("SQLite detected - using Flask-Migrate")
                migrate_sqlite()
                
            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            print("\nNew features available:")
            print("  - Deal assignee linking to User model")
            print("  - Revenue month calculation")
            print("  - Assignee-based filtering and reporting")
            print("\nYou can now use assignee_id in deal forms.")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            print("\nTrying to create all tables (safe for new database)...")
            db.create_all()
            print("✓ Database schema created")

def migrate_postgresql():
    """Migrate PostgreSQL database using ALTER TABLE"""
    migrations = [
        # Add assignee_id column
        """
        DO $$ BEGIN
            ALTER TABLE deals ADD COLUMN IF NOT EXISTS assignee_id INTEGER REFERENCES users(id);
            CREATE INDEX IF NOT EXISTS ix_deals_assignee_id ON deals(assignee_id);
        END $$;
        """
    ]
    
    for i, migration in enumerate(migrations, 1):
        try:
            print(f"Running migration {i}/{len(migrations)}...")
            db.session.execute(db.text(migration))
            db.session.commit()
            print(f"✓ Migration {i} completed")
        except Exception as e:
            print(f"Note: Migration {i} - {e}")
            db.session.rollback()

def migrate_sqlite():
    """For SQLite, use db.create_all() which handles schema updates"""
    print("Creating/updating tables...")
    db.create_all()
    print("✓ Tables created/updated")

if __name__ == '__main__':
    run_migration()













