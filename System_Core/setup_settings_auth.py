import sqlite3
import os

DB_PATH = 'consultancy.db'

def setup_settings_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create Settings Table
    print("Creating Settings table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Seed Default Settings
    defaults = {
        'system_name': 'Consultancy OS',
        'system_logo': '/portal/assets/logo_placeholder.png', # We will need a placeholder or handle upload
        'theme': 'light'
    }
    
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO Settings (key, value) VALUES (?, ?)", (k, v))


    # 2. Create Users Table
    print("Creating Users table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT, -- In real app, hash this! For demo, plain/simple hash.
            role TEXT,
            full_name TEXT,
            email TEXT
        )
    ''')

    # Seed Default Admin
    # Check if admin exists
    cursor.execute("SELECT id FROM Users WHERE username = 'admin'")
    if not cursor.fetchone():
        import uuid
        uid = str(uuid.uuid4())
        print(f"Creating default admin user (id: {uid})...")
        cursor.execute('''
            INSERT INTO Users (id, username, password, role, full_name, email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (uid, 'admin', 'admin123', 'System Admin', 'System Administrator', 'admin@consultancy.local'))

    conn.commit()
    conn.close()
    print("Settings and Auth tables setup complete.")

if __name__ == '__main__':
    setup_settings_db()
