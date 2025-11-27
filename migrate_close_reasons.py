#!/usr/bin/env python3
"""
Migration script for v2.6.0: Add win/loss reason tracking to deals

This migration:
1. Renames existing win_reason → win_reason_detail (preserves data)
2. Renames existing lost_reason → lost_reason_detail (preserves data)
3. Adds new columns: win_reason_category, lost_reason_category, closed_at
4. Normalizes status values: '進行中'→'OPEN', '受注'→'WON', '失注'→'LOST'

Non-destructive: All existing data is preserved.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from datetime import datetime

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

def get_db_type():
    """Detect database type"""
    return 'sqlite' if 'sqlite' in DATABASE_URL else 'postgresql'

def column_exists(table_name, column_name):
    """Check if column exists in table"""
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_sqlite(connection):
    """SQLite-specific migration using table recreation"""
    print("Executing SQLite migration...")
    
    # Check if old columns exist
    has_old_win_reason = column_exists('deals', 'win_reason')
    has_old_lost_reason = column_exists('deals', 'lost_reason')
    
    # Get existing columns to preserve order
    existing_columns = inspector.get_columns('deals')
    
    # Create temporary table with new schema
    connection.execute(text("""
        CREATE TABLE deals_new (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            stage VARCHAR(50) NOT NULL,
            amount REAL DEFAULT 0,
            status VARCHAR(50) NOT NULL,
            note TEXT,
            created_at TIMESTAMP,
            stage_entered_at TIMESTAMP,
            assignee VARCHAR(100),
            meeting_minutes TEXT,
            next_action TEXT,
            heat_score VARCHAR(20) DEFAULT 'C',
            appointment_date DATE,
            win_reason_category VARCHAR(100),
            win_reason_detail TEXT,
            lost_reason_category VARCHAR(100),
            lost_reason_detail TEXT,
            closed_at TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """))
    
    # Build SELECT statement to copy data
    # If old columns exist, copy them to new *_detail columns
    select_columns = []
    for col in existing_columns:
        if col['name'] == 'win_reason' and has_old_win_reason:
            select_columns.append('win_reason as win_reason_detail')
        elif col['name'] == 'lost_reason' and has_old_lost_reason:
            select_columns.append('lost_reason as lost_reason_detail')
        elif col['name'] not in ['win_reason', 'lost_reason']:
            select_columns.append(col['name'])
    
    # Add NULL for new columns that don't exist in old table
    if not has_old_win_reason:
        select_columns.append('NULL as win_reason_detail')
    if not has_old_lost_reason:
        select_columns.append('NULL as lost_reason_detail')
    
    select_columns.extend([
        'NULL as win_reason_category',
        'NULL as lost_reason_category',
        'NULL as closed_at'
    ])
    
    # Copy data from old table to new table
    connection.execute(text(f"""
        INSERT INTO deals_new ({', '.join([c.replace(' as ', '') for c in select_columns])})
        SELECT {', '.join(select_columns)}
        FROM deals
    """))
    
    # Drop old table and rename new table
    connection.execute(text("DROP TABLE deals"))
    connection.execute(text("ALTER TABLE deals_new RENAME TO deals"))
    
    # Create indexes
    connection.execute(text("CREATE INDEX ix_deals_stage ON deals(stage)"))
    connection.execute(text("CREATE INDEX ix_deals_status ON deals(status)"))
    connection.execute(text("CREATE INDEX ix_deals_assignee ON deals(assignee)"))
    connection.execute(text("CREATE INDEX ix_deals_heat_score ON deals(heat_score)"))
    connection.execute(text("CREATE INDEX ix_deals_appointment_date ON deals(appointment_date)"))
    connection.execute(text("CREATE INDEX ix_deals_win_reason_category ON deals(win_reason_category)"))
    connection.execute(text("CREATE INDEX ix_deals_lost_reason_category ON deals(lost_reason_category)"))
    connection.execute(text("CREATE INDEX ix_deals_closed_at ON deals(closed_at)"))
    
    print("✓ SQLite table recreated with new schema")

def migrate_postgresql(connection):
    """PostgreSQL-specific migration using ALTER TABLE"""
    print("Executing PostgreSQL migration...")
    
    # Check if old columns exist
    has_old_win_reason = column_exists('deals', 'win_reason')
    has_old_lost_reason = column_exists('deals', 'lost_reason')
    
    # Rename existing columns if they exist
    if has_old_win_reason and not column_exists('deals', 'win_reason_detail'):
        connection.execute(text("ALTER TABLE deals RENAME COLUMN win_reason TO win_reason_detail"))
        print("✓ Renamed win_reason → win_reason_detail")
    
    if has_old_lost_reason and not column_exists('deals', 'lost_reason_detail'):
        connection.execute(text("ALTER TABLE deals RENAME COLUMN lost_reason TO lost_reason_detail"))
        print("✓ Renamed lost_reason → lost_reason_detail")
    
    # Add new columns if they don't exist
    if not column_exists('deals', 'win_reason_category'):
        connection.execute(text("ALTER TABLE deals ADD COLUMN win_reason_category VARCHAR(100)"))
        connection.execute(text("CREATE INDEX ix_deals_win_reason_category ON deals(win_reason_category)"))
        print("✓ Added win_reason_category")
    
    if not column_exists('deals', 'lost_reason_category'):
        connection.execute(text("ALTER TABLE deals ADD COLUMN lost_reason_category VARCHAR(100)"))
        connection.execute(text("CREATE INDEX ix_deals_lost_reason_category ON deals(lost_reason_category)"))
        print("✓ Added lost_reason_category")
    
    if not column_exists('deals', 'closed_at'):
        connection.execute(text("ALTER TABLE deals ADD COLUMN closed_at TIMESTAMP"))
        connection.execute(text("CREATE INDEX ix_deals_closed_at ON deals(closed_at)"))
        print("✓ Added closed_at")
    
    if not has_old_win_reason and not column_exists('deals', 'win_reason_detail'):
        connection.execute(text("ALTER TABLE deals ADD COLUMN win_reason_detail TEXT"))
        print("✓ Added win_reason_detail")
    
    if not has_old_lost_reason and not column_exists('deals', 'lost_reason_detail'):
        connection.execute(text("ALTER TABLE deals ADD COLUMN lost_reason_detail TEXT"))
        print("✓ Added lost_reason_detail")

def normalize_status_values(connection):
    """Normalize status values from Japanese to English"""
    print("\nNormalizing status values...")
    
    # Mapping: Japanese → English
    status_mapping = {
        '進行中': 'OPEN',
        '受注': 'WON',
        '失注': 'LOST'
    }
    
    for old_status, new_status in status_mapping.items():
        result = connection.execute(
            text("UPDATE deals SET status = :new_status WHERE status = :old_status"),
            {'new_status': new_status, 'old_status': old_status}
        )
        if result.rowcount > 0:
            print(f"✓ Updated {result.rowcount} deals: '{old_status}' → '{new_status}'")
    
    # Set closed_at for already closed deals (WON/LOST) if not already set
    result = connection.execute(text("""
        UPDATE deals 
        SET closed_at = created_at 
        WHERE status IN ('WON', 'LOST') 
        AND closed_at IS NULL
    """))
    if result.rowcount > 0:
        print(f"✓ Set closed_at for {result.rowcount} already closed deals")

def main():
    """Execute migration"""
    db_type = get_db_type()
    print(f"\nMigration: Add win/loss reason tracking (v2.6.0)")
    print(f"Database: {db_type}")
    print("=" * 60)
    
    try:
        with engine.begin() as connection:
            # Execute database-specific migration
            if db_type == 'sqlite':
                migrate_sqlite(connection)
            else:
                migrate_postgresql(connection)
            
            # Normalize status values (common for both)
            normalize_status_values(connection)
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("\nNew columns added:")
        print("  - win_reason_category (indexed)")
        print("  - win_reason_detail")
        print("  - lost_reason_category (indexed)")
        print("  - lost_reason_detail")
        print("  - closed_at (indexed)")
        print("\nStatus values normalized:")
        print("  '進行中' → 'OPEN'")
        print("  '受注' → 'WON'")
        print("  '失注' → 'LOST'")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
