
import sqlite3
import uuid
import hashlib

DB_PATH = r'd:\Custom_System_Copy\System_Core\consultancy.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creating Admin User...")
    # Ensure table exists just in case
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "Users" (
        "id" TEXT PRIMARY KEY,
        "username" TEXT UNIQUE,
        "password_hash" TEXT,
        "full_name" TEXT,
        "role" TEXT
    );
    """)
    
    # Create Admin
    try:
        cursor.execute("DELETE FROM Users WHERE username='admin'")
        cursor.execute("""
            INSERT INTO Users (id, username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), "admin", hash_password("admin123"), "System Administrator", "Administrator"))
        conn.commit()
        print("SUCCESS: Admin user created (User: admin, Pass: admin123)")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin()
