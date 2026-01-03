
import sqlite3

DB_PATH = 'd:/Custom_System_Copy/System_Core/consultancy.db'

def migrate_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Add email column if missing
        cursor.execute("PRAGMA table_info(Users)")
        cols = [row[1] for row in cursor.fetchall()]
        
        if 'email' not in cols:
            print("Adding email column...")
            cursor.execute("ALTER TABLE Users ADD COLUMN email TEXT")
        else:
            print("email column already exists.")

        # 2. Check password column name
        if 'password' not in cols and 'password_hash' in cols:
            print("Using 'password_hash' column.")
            # No change needed to schema, just code needs to update.
        elif 'password' in cols:
             print("Schema uses 'password'.")

        conn.commit()
        print("Migration complete.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
