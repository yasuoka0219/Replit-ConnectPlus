"""
Automatic backup utility for CONNECT+ CRM
Handles database backups and file management
"""
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json
from flask import current_app
from database import db


def get_backup_directory():
    """Get or create backup directory"""
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def backup_sqlite_database(db_path, backup_dir=None):
    """
    Backup SQLite database
    
    Args:
        db_path (str): Path to SQLite database file
        backup_dir (Path, optional): Backup directory (default: backups/)
        
    Returns:
        str: Path to backup file
    """
    if backup_dir is None:
        backup_dir = get_backup_directory()
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'connectplus_backup_{timestamp}.db'
    backup_path = backup_dir / backup_filename
    
    try:
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        # Also create a compressed copy
        import gzip
        compressed_path = backup_dir / f'{backup_filename}.gz'
        with open(db_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Create metadata file
        metadata = {
            'timestamp': timestamp,
            'database_path': str(db_path),
            'backup_file': backup_filename,
            'compressed_file': f'{backup_filename}.gz',
            'size': os.path.getsize(backup_path),
            'compressed_size': os.path.getsize(compressed_path)
        }
        
        metadata_path = backup_dir / f'{backup_filename}.meta.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Database backup created: {backup_path}")
        return str(backup_path)
    except Exception as e:
        print(f"✗ Backup failed: {e}")
        raise


def backup_postgresql_database(database_url, backup_dir=None):
    """
    Backup PostgreSQL database using pg_dump
    
    Args:
        database_url (str): PostgreSQL connection URL
        backup_dir (Path, optional): Backup directory (default: backups/)
        
    Returns:
        str: Path to backup file
    """
    if backup_dir is None:
        backup_dir = get_backup_directory()
    
    import subprocess
    from urllib.parse import urlparse
    
    # Parse database URL
    parsed = urlparse(database_url)
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'connectplus_backup_{timestamp}.sql'
    backup_path = backup_dir / backup_filename
    
    try:
        # Build pg_dump command
        pg_dump_cmd = [
            'pg_dump',
            '-h', parsed.hostname or 'localhost',
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path[1:] if parsed.path else 'connectplus',
            '-F', 'c',  # Custom format (compressed)
            '-f', str(backup_path)
        ]
        
        # Set password from URL
        env = os.environ.copy()
        if parsed.password:
            env['PGPASSWORD'] = parsed.password
        
        # Run pg_dump
        result = subprocess.run(pg_dump_cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"pg_dump failed: {result.stderr}")
        
        # Create metadata file
        metadata = {
            'timestamp': timestamp,
            'database_url': database_url.replace(parsed.password or '', '***') if parsed.password else database_url,
            'backup_file': backup_filename,
            'size': os.path.getsize(backup_path)
        }
        
        metadata_path = backup_dir / f'{backup_filename}.meta.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ PostgreSQL backup created: {backup_path}")
        return str(backup_path)
    except FileNotFoundError:
        raise Exception("pg_dump command not found. Please install PostgreSQL client tools.")
    except Exception as e:
        print(f"✗ Backup failed: {e}")
        raise


def create_backup():
    """
    Create database backup based on database type
    
    Returns:
        str: Path to backup file
    """
    database_url = os.environ.get('DATABASE_URL', '')
    
    if 'sqlite' in database_url.lower():
        # SQLite backup
        db_path = database_url.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            # Relative path
            db_path = os.path.join(os.getcwd(), db_path)
        return backup_sqlite_database(db_path)
    elif 'postgresql' in database_url.lower() or 'postgres' in database_url.lower():
        # PostgreSQL backup
        return backup_postgresql_database(database_url)
    else:
        raise Exception(f"Unsupported database type: {database_url}")


def cleanup_old_backups(keep_days=30, backup_dir=None):
    """
    Clean up old backup files
    
    Args:
        keep_days (int): Number of days to keep backups
        backup_dir (Path, optional): Backup directory (default: backups/)
    """
    if backup_dir is None:
        backup_dir = get_backup_directory()
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    deleted_count = 0
    
    try:
        for file_path in backup_dir.glob('connectplus_backup_*'):
            # Skip if file is too new
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time > cutoff_date:
                continue
            
            # Delete old backup file
            try:
                file_path.unlink()
                deleted_count += 1
                print(f"  Deleted old backup: {file_path.name}")
            except Exception as e:
                print(f"  Failed to delete {file_path.name}: {e}")
        
        print(f"✓ Cleaned up {deleted_count} old backup(s)")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")


def list_backups(backup_dir=None):
    """
    List all available backups
    
    Args:
        backup_dir (Path, optional): Backup directory (default: backups/)
        
    Returns:
        list: List of backup metadata dictionaries
    """
    if backup_dir is None:
        backup_dir = get_backup_directory()
    
    backups = []
    
    # Find all metadata files
    for meta_file in backup_dir.glob('*.meta.json'):
        try:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
                backup_file = backup_dir / metadata.get('backup_file', '')
                if backup_file.exists():
                    metadata['backup_path'] = str(backup_file)
                    metadata['exists'] = True
                    metadata['file_size'] = os.path.getsize(backup_file)
                else:
                    metadata['exists'] = False
                backups.append(metadata)
        except Exception as e:
            print(f"  Failed to read metadata {meta_file}: {e}")
    
    # Sort by timestamp (newest first)
    backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return backups


def restore_backup(backup_path, database_url=None):
    """
    Restore database from backup
    
    Args:
        backup_path (str): Path to backup file
        database_url (str, optional): Database URL (default: from environment)
        
    Note: This is a dangerous operation and should be used with caution
    """
    if database_url is None:
        database_url = os.environ.get('DATABASE_URL', '')
    
    # This is a placeholder - actual restore implementation would depend on database type
    # and should include proper error handling and confirmation
    raise NotImplementedError("Database restore functionality should be implemented carefully")





