"""
Migration script to add Google Calendar integration tables and columns
"""
from database import db
from models import Task, Activity, GoogleCalendarConnection
from sqlalchemy import text
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

def run_google_calendar_migration():
    """Run migration to add Google Calendar integration support"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        database_url = os.environ.get('DATABASE_URL', '')
        
        # Check if using SQLite or PostgreSQL
        is_sqlite = not database_url or 'sqlite' in database_url.lower()
        
        print("=" * 60)
        print("Googleカレンダー連携用マイグレーションを開始します")
        print("=" * 60)
        
        try:
            # Create GoogleCalendarConnection table
            print("\n1. GoogleCalendarConnectionテーブルを作成中...")
            try:
                db.create_all()  # This will create all tables including GoogleCalendarConnection
                print("✓ GoogleCalendarConnectionテーブルの作成を確認しました")
            except Exception as e:
                print(f"⚠ テーブル作成エラー（既に存在する可能性があります）: {e}")
            
            # Add google_calendar_event_id column to tasks table
            print("\n2. tasksテーブルにgoogle_calendar_event_idカラムを追加中...")
            try:
                if is_sqlite:
                    # SQLite - check if column exists first
                    result = db.session.execute(text("PRAGMA table_info(tasks)"))
                    columns = [row[1] for row in result]
                    if 'google_calendar_event_id' not in columns:
                        db.session.execute(text("""
                            ALTER TABLE tasks 
                            ADD COLUMN google_calendar_event_id VARCHAR(255)
                        """))
                        db.session.commit()
                        print("✓ tasksテーブルにgoogle_calendar_event_idカラムを追加しました")
                    else:
                        print("✓ google_calendar_event_idカラムは既に存在します")
                else:
                    # PostgreSQL - check if column exists first
                    result = db.session.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='tasks' AND column_name='google_calendar_event_id'
                    """))
                    if not result.fetchone():
                        db.session.execute(text("""
                            ALTER TABLE tasks 
                            ADD COLUMN google_calendar_event_id VARCHAR(255)
                        """))
                        db.session.commit()
                        print("✓ tasksテーブルにgoogle_calendar_event_idカラムを追加しました")
                    else:
                        print("✓ google_calendar_event_idカラムは既に存在します")
            except Exception as e:
                print(f"⚠ カラム追加エラー（既に存在する可能性があります）: {e}")
                db.session.rollback()
            
            # Add index for google_calendar_event_id in tasks
            print("\n3. tasksテーブルにインデックスを追加中...")
            try:
                if is_sqlite:
                    # SQLite doesn't support CREATE INDEX IF NOT EXISTS in older versions
                    # Try to create index (will fail silently if exists)
                    try:
                        db.session.execute(text("""
                            CREATE INDEX IF NOT EXISTS ix_tasks_google_calendar_event_id 
                            ON tasks(google_calendar_event_id)
                        """))
                        db.session.commit()
                        print("✓ インデックスを追加しました")
                    except:
                        print("✓ インデックスは既に存在するか、追加不要です")
                else:
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_tasks_google_calendar_event_id 
                        ON tasks(google_calendar_event_id)
                    """))
                    db.session.commit()
                    print("✓ インデックスを追加しました")
            except Exception as e:
                print(f"⚠ インデックス追加エラー（既に存在する可能性があります）: {e}")
                db.session.rollback()
            
            # Add google_calendar_event_id column to activities table
            print("\n4. activitiesテーブルにgoogle_calendar_event_idカラムを追加中...")
            try:
                if is_sqlite:
                    result = db.session.execute(text("PRAGMA table_info(activities)"))
                    columns = [row[1] for row in result]
                    if 'google_calendar_event_id' not in columns:
                        db.session.execute(text("""
                            ALTER TABLE activities 
                            ADD COLUMN google_calendar_event_id VARCHAR(255)
                        """))
                        db.session.commit()
                        print("✓ activitiesテーブルにgoogle_calendar_event_idカラムを追加しました")
                    else:
                        print("✓ google_calendar_event_idカラムは既に存在します")
                else:
                    result = db.session.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='activities' AND column_name='google_calendar_event_id'
                    """))
                    if not result.fetchone():
                        db.session.execute(text("""
                            ALTER TABLE activities 
                            ADD COLUMN google_calendar_event_id VARCHAR(255)
                        """))
                        db.session.commit()
                        print("✓ activitiesテーブルにgoogle_calendar_event_idカラムを追加しました")
                    else:
                        print("✓ google_calendar_event_idカラムは既に存在します")
            except Exception as e:
                print(f"⚠ カラム追加エラー（既に存在する可能性があります）: {e}")
                db.session.rollback()
            
            # Add index for google_calendar_event_id in activities
            print("\n5. activitiesテーブルにインデックスを追加中...")
            try:
                if is_sqlite:
                    try:
                        db.session.execute(text("""
                            CREATE INDEX IF NOT EXISTS ix_activities_google_calendar_event_id 
                            ON activities(google_calendar_event_id)
                        """))
                        db.session.commit()
                        print("✓ インデックスを追加しました")
                    except:
                        print("✓ インデックスは既に存在するか、追加不要です")
                else:
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS ix_activities_google_calendar_event_id 
                        ON activities(google_calendar_event_id)
                    """))
                    db.session.commit()
                    print("✓ インデックスを追加しました")
            except Exception as e:
                print(f"⚠ インデックス追加エラー（既に存在する可能性があります）: {e}")
                db.session.rollback()
            
            print("\n" + "=" * 60)
            print("マイグレーションが完了しました！")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\nエラーが発生しました: {e}")
            raise


if __name__ == '__main__':
    run_google_calendar_migration()

