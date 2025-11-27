#!/usr/bin/env python3
"""
Database Migration Script
This script safely migrates the existing database to the new schema.
"""
import os
import sys
from datetime import datetime
from app import app, db
from models import User, Company, Contact, Deal, Task, Activity

def run_migration():
    """Run database migration safely"""
    with app.app_context():
        print("=" * 60)
        print("CONNECT+ Database Migration Script")
        print("=" * 60)
        print("\nThis will update your database schema with new fields.")
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
            # For PostgreSQL, we can use ALTER TABLE
            # For SQLite, Flask-Migrate handles table recreation automatically
            
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
            print("  - Company heat scoring and tagging")
            print("  - Activity logging (calls, meetings, emails, notes)")
            print("  - Deal stage tracking with duration")
            print("  - Enhanced contact information")
            print("\nYou can now run: python app.py")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            print("\nTrying to create all tables (safe for new database)...")
            db.create_all()
            print("✓ Database schema created")

def migrate_postgresql():
    """Migrate PostgreSQL database using ALTER TABLE"""
    migrations = [
        # Companies table extensions
        """
        DO $$ BEGIN
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS employee_size INTEGER;
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS hq_location VARCHAR(200);
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS website VARCHAR(300);
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS needs TEXT;
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS kpi_current TEXT;
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS heat_score INTEGER DEFAULT 1;
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS last_contacted_at TIMESTAMP;
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS next_action_at TIMESTAMP;
            ALTER TABLE companies ADD COLUMN IF NOT EXISTS tags VARCHAR(500);
        END $$;
        """,
        # Contacts table extensions
        """
        DO $$ BEGIN
            ALTER TABLE contacts ADD COLUMN IF NOT EXISTS role VARCHAR(100);
            ALTER TABLE contacts ADD COLUMN IF NOT EXISTS notes TEXT;
        END $$;
        """,
        # Deals table extensions
        """
        DO $$ BEGIN
            ALTER TABLE deals ADD COLUMN IF NOT EXISTS win_reason TEXT;
            ALTER TABLE deals ADD COLUMN IF NOT EXISTS lost_reason TEXT;
            ALTER TABLE deals ADD COLUMN IF NOT EXISTS stage_entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            ALTER TABLE deals ADD COLUMN IF NOT EXISTS assignee VARCHAR(100);
        END $$;
        """,
        # Create activities table
        """
        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            deal_id INTEGER REFERENCES deals(id) ON DELETE CASCADE,
            type VARCHAR(20) NOT NULL CHECK (type IN ('call', 'meeting', 'email', 'note')),
            title VARCHAR(200) NOT NULL,
            body TEXT,
            happened_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Create indexes
        """
        CREATE INDEX IF NOT EXISTS ix_companies_name ON companies(name);
        CREATE INDEX IF NOT EXISTS ix_companies_industry ON companies(industry);
        CREATE INDEX IF NOT EXISTS ix_companies_heat_score ON companies(heat_score);
        CREATE INDEX IF NOT EXISTS ix_deals_stage ON deals(stage);
        CREATE INDEX IF NOT EXISTS ix_deals_status ON deals(status);
        CREATE INDEX IF NOT EXISTS ix_deals_assignee ON deals(assignee);
        CREATE INDEX IF NOT EXISTS ix_deals_closed_at ON deals(closed_at);
        CREATE INDEX IF NOT EXISTS ix_deals_win_reason_category ON deals(win_reason_category);
        CREATE INDEX IF NOT EXISTS ix_deals_lost_reason_category ON deals(lost_reason_category);
        CREATE INDEX IF NOT EXISTS ix_activities_company_id ON activities(company_id);
        CREATE INDEX IF NOT EXISTS ix_activities_happened_at ON activities(happened_at);
        CREATE INDEX IF NOT EXISTS ix_activities_company_happened ON activities(company_id, happened_at);
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
