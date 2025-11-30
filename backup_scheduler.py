"""
Backup scheduler for CONNECT+ CRM
Runs automated database backups on schedule
"""
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Import backup utilities
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.backup import create_backup, cleanup_old_backups

# Backup configuration
BACKUP_INTERVAL_HOURS = int(os.environ.get('BACKUP_INTERVAL_HOURS', '24'))  # Default: daily
BACKUP_KEEP_DAYS = int(os.environ.get('BACKUP_KEEP_DAYS', '30'))  # Default: keep 30 days


def run_backup():
    """Run backup job"""
    try:
        print(f"[{datetime.now()}] Starting scheduled backup...")
        backup_path = create_backup()
        print(f"[{datetime.now()}] Backup completed: {backup_path}")
        
        # Cleanup old backups
        print(f"[{datetime.now()}] Cleaning up old backups...")
        cleanup_old_backups(keep_days=BACKUP_KEEP_DAYS)
        print(f"[{datetime.now()}] Cleanup completed")
    except Exception as e:
        print(f"[{datetime.now()}] Backup failed: {e}")


def start_scheduler():
    """Start backup scheduler"""
    scheduler = BackgroundScheduler()
    
    # Schedule daily backup at 2 AM
    scheduler.add_job(
        run_backup,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_backup',
        name='Daily database backup',
        replace_existing=True
    )
    
    scheduler.start()
    print(f"[{datetime.now()}] Backup scheduler started (daily at 2:00 AM)")
    print(f"[{datetime.now()}] Backup retention: {BACKUP_KEEP_DAYS} days")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print(f"[{datetime.now()}] Backup scheduler stopped")


if __name__ == '__main__':
    print("=" * 60)
    print("CONNECT+ CRM - Backup Scheduler")
    print("=" * 60)
    
    # Run initial backup on start (optional)
    if os.environ.get('RUN_INITIAL_BACKUP', 'False').lower() == 'true':
        print("Running initial backup...")
        run_backup()
    
    # Start scheduler
    start_scheduler()





