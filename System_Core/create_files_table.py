
import sqlite3
import os

DB_PATH = r'd:\Custom_System_Copy\System_Core\consultancy.db'

def setup_files_table():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Files Table
    print("Creating Files table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Files (
            id TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            parent_doctype TEXT,
            parent_id TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Files table created successfully.")

if __name__ == "__main__":
    setup_files_table()
