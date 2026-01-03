
import sqlite3
import hashlib

DB_PATH = r'd:\Custom_System_Copy\System_Core\consultancy.db'

def check_users():
    print(f"Checking {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'")
        if not cursor.fetchone():
            print("ERROR: Users table does not exist!")
            return

        # Check users
        cursor.execute("SELECT username, password_hash, full_name, role FROM Users")
        rows = cursor.fetchall()
        if not rows:
            print("ERROR: Users table is empty!")
        else:
            print("Found Users:")
            for row in rows:
                print(f"User: {row[0]}, Role: {row[3]}, Hash: {row[1]}")
                
        # Verify admin password manually
        expected_hash = hashlib.sha256("admin123".encode()).hexdigest()
        print(f"\nExpected Hash for 'admin123': {expected_hash}")
        
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    check_users()
