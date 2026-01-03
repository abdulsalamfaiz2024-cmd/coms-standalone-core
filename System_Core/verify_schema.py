
import sqlite3
import os

DB_PATH = 'd:/Custom_System_Copy/System_Core/consultancy.db'

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found: {tables}")

        if 'Settings' not in tables:
            print("CRITICAL: Settings table MISSING")
        else:
            cursor.execute("PRAGMA table_info(Settings)")
            cols = cursor.fetchall()
            print(f"Settings Columns: {cols}")

        if 'Users' not in tables:
            print("CRITICAL: Users table MISSING")
        else:
            cursor.execute("PRAGMA table_info(Users)")
            cols = cursor.fetchall()
            print(f"Users Columns: {cols}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
