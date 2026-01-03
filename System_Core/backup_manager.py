
import shutil
import os
import datetime
import sqlite3
from pathlib import Path

# Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'consultancy.db')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
MAX_BACKUPS = 10

def ensure_backup_dir():
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)

def create_timestamped_backup():
    """
    Creates a hot backup of the SQLite database using the standard backup API
    to ensure data integrity even if the DB is being accessed.
    """
    ensure_backup_dir()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"consultancy_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        # Connect to existing DB
        src = sqlite3.connect(DB_PATH)
        # Connect to backup DB
        dst = sqlite3.connect(backup_path)
        
        # Perform backup
        with dst:
            src.backup(dst)
            
        dst.close()
        src.close()
        
        print(f"SUCCESS: Backup created at {backup_path}")
        rotate_backups()
        return {"status": "success", "file": backup_filename, "path": backup_path, "timestamp": timestamp}
        
    except Exception as e:
        print(f"ERROR: Backup failed - {str(e)}")
        return {"status": "error", "message": str(e)}

def rotate_backups():
    """
    Maintains only the last MAX_BACKUPS files to save space.
    """
    files = sorted(Path(BACKUP_DIR).glob('*.db'), key=os.path.getmtime)
    if len(files) > MAX_BACKUPS:
        for f in files[:-MAX_BACKUPS]:
            print(f"ROTATION: Deleting old backup {f.name}")
            os.remove(f)

if __name__ == "__main__":
    create_timestamped_backup()
