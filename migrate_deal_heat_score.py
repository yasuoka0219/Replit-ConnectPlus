#!/usr/bin/env python3
"""
Migration: Add heat_score to deals table
Date: 2025-11-12
Description: Adds heat_score column to deals table for per-deal temperature tracking
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
    """Add heat_score column to deals table"""
    
    with engine.connect() as conn:
        print("Starting migration: Add heat_score to deals...")
        
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'deals' 
            AND column_name = 'heat_score'
        """)
        
        result = conn.execute(check_query)
        if result.fetchone():
            print("✓ heat_score column already exists in deals table. Skipping migration.")
            return
        
        # Add heat_score column to deals
        print("Adding heat_score column to deals table...")
        conn.execute(text("""
            ALTER TABLE deals 
            ADD COLUMN heat_score VARCHAR(20) DEFAULT 'C'
        """))
        conn.commit()
        
        # Create index on heat_score
        print("Creating index on deals.heat_score...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_deals_heat_score 
            ON deals(heat_score)
        """))
        conn.commit()
        
        print("✓ Migration completed successfully!")
        print("  - Added heat_score column to deals (default: 'C')")
        print("  - Created index on deals.heat_score")

if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print(f"ERROR during migration: {e}")
        raise
