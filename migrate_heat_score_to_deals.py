#!/usr/bin/env python3
"""
Migration: Move heat_score from companies to deals
Date: 2025-11-12
Description: 
1. Copies heat_score from companies to their related deals
2. Drops heat_score column from companies table
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

engine = create_engine(DATABASE_URL)

def migrate():
    """Move heat_score from companies to deals"""
    
    with engine.connect() as conn:
        print("Starting migration: Move heat_score from companies to deals...")
        
        # Check if deals.heat_score column exists
        check_deals_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'deals' 
            AND column_name = 'heat_score'
        """)
        
        result = conn.execute(check_deals_query)
        if not result.fetchone():
            print("ERROR: deals.heat_score column does not exist. Run migrate_deal_heat_score.py first.")
            return
        
        # Check if companies.heat_score column exists
        check_companies_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'companies' 
            AND column_name = 'heat_score'
        """)
        
        result = conn.execute(check_companies_query)
        if not result.fetchone():
            print("✓ companies.heat_score column already removed. Migration already completed.")
            return
        
        # Copy heat_score from companies to deals
        print("Copying heat_score from companies to deals...")
        copy_query = text("""
            UPDATE deals 
            SET heat_score = COALESCE(companies.heat_score, 'C')
            FROM companies 
            WHERE deals.company_id = companies.id
        """)
        conn.execute(copy_query)
        conn.commit()
        
        print("✓ Copied heat_score data from companies to deals")
        
        # Drop heat_score column from companies
        print("Dropping heat_score column from companies table...")
        conn.execute(text("""
            DROP INDEX IF EXISTS ix_companies_heat_score
        """))
        conn.commit()
        
        conn.execute(text("""
            ALTER TABLE companies 
            DROP COLUMN heat_score
        """))
        conn.commit()
        
        print("✓ Migration completed successfully!")
        print("  - Copied heat_score from companies to all related deals")
        print("  - Dropped heat_score column from companies table")

if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print(f"ERROR during migration: {e}")
        raise
