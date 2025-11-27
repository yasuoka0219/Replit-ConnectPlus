"""
Migration script to add meeting_minutes and next_action fields to deals table
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'deals' 
                AND column_name IN ('meeting_minutes', 'next_action')
            """))
            existing_columns = {row[0] for row in result}
            
            # Add meeting_minutes if it doesn't exist
            if 'meeting_minutes' not in existing_columns:
                print("📝 Adding meeting_minutes column...")
                conn.execute(text("""
                    ALTER TABLE deals 
                    ADD COLUMN meeting_minutes TEXT
                """))
                conn.commit()
                print("✅ meeting_minutes column added")
            else:
                print("ℹ️  meeting_minutes column already exists")
            
            # Add next_action if it doesn't exist
            if 'next_action' not in existing_columns:
                print("📝 Adding next_action column...")
                conn.execute(text("""
                    ALTER TABLE deals 
                    ADD COLUMN next_action TEXT
                """))
                conn.commit()
                print("✅ next_action column added")
            else:
                print("ℹ️  next_action column already exists")
            
            print("\n✅ Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        engine.dispose()

if __name__ == '__main__':
    print("🔄 Starting migration: Add meeting_minutes and next_action to deals")
    print("=" * 60)
    migrate()
