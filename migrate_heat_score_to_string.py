"""
Migration script to convert heat_score from Integer to String (A/B/C/ネタ)
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
            print("🔄 Starting migration: Convert heat_score from Integer to String")
            print("=" * 60)
            
            # Step 1: Add temporary column
            print("📝 Adding temporary heat_score_new column...")
            conn.execute(text("""
                ALTER TABLE companies 
                ADD COLUMN IF NOT EXISTS heat_score_new VARCHAR(20)
            """))
            conn.commit()
            print("✅ Temporary column added")
            
            # Step 2: Migrate data with conversion logic
            print("📝 Converting existing heat_score values...")
            conn.execute(text("""
                UPDATE companies
                SET heat_score_new = CASE 
                    WHEN heat_score >= 4 THEN 'A'
                    WHEN heat_score = 3 THEN 'B'
                    WHEN heat_score = 2 THEN 'C'
                    WHEN heat_score = 1 THEN 'ネタ'
                    ELSE 'C'
                END
                WHERE heat_score_new IS NULL
            """))
            conn.commit()
            print("✅ Data converted")
            
            # Step 3: Drop old column
            print("📝 Dropping old heat_score column...")
            conn.execute(text("""
                ALTER TABLE companies 
                DROP COLUMN IF EXISTS heat_score
            """))
            conn.commit()
            print("✅ Old column dropped")
            
            # Step 4: Rename new column
            print("📝 Renaming heat_score_new to heat_score...")
            conn.execute(text("""
                ALTER TABLE companies 
                RENAME COLUMN heat_score_new TO heat_score
            """))
            conn.commit()
            print("✅ Column renamed")
            
            # Step 5: Set default value
            print("📝 Setting default value to 'C'...")
            conn.execute(text("""
                ALTER TABLE companies 
                ALTER COLUMN heat_score SET DEFAULT 'C'
            """))
            conn.commit()
            print("✅ Default value set")
            
            # Step 6: Recreate index
            print("📝 Recreating index...")
            conn.execute(text("""
                DROP INDEX IF EXISTS ix_companies_heat_score
            """))
            conn.execute(text("""
                CREATE INDEX ix_companies_heat_score ON companies(heat_score)
            """))
            conn.commit()
            print("✅ Index recreated")
            
            # Verify migration
            print("\n📊 Verifying migration...")
            result = conn.execute(text("""
                SELECT heat_score, COUNT(*) as count
                FROM companies
                GROUP BY heat_score
                ORDER BY heat_score
            """))
            print("\nHeat score distribution:")
            for row in result:
                print(f"  {row[0]}: {row[1]} companies")
            
            print("\n✅ Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()

if __name__ == '__main__':
    migrate()
