import sqlite3
import hashlib

conn = sqlite3.connect('System_Core/consultancy.db')
cursor = conn.cursor()

# Create a test consultant user
pwd_hash = hashlib.sha256('consultant123'.encode()).hexdigest()
cursor.execute('''
    INSERT OR REPLACE INTO Users (id, username, password_hash, role, full_name, email)
    VALUES ('cons-001', 'consultant', ?, 'Consultant', 'Test Consultant', 'consultant@test.com')
''', (pwd_hash,))

# Create a test viewer user
pwd_hash2 = hashlib.sha256('viewer123'.encode()).hexdigest()
cursor.execute('''
    INSERT OR REPLACE INTO Users (id, username, password_hash, role, full_name, email)
    VALUES ('view-001', 'viewer', ?, 'Viewer', 'Test Viewer', 'viewer@test.com')
''', (pwd_hash2,))

# Update admin role to Admin
cursor.execute("UPDATE Users SET role = 'Admin' WHERE username = 'admin'")

conn.commit()
print('Test users created:')
print('  - admin / admin123 (Admin)')
print('  - consultant / consultant123 (Consultant)')
print('  - viewer / viewer123 (Viewer)')
conn.close()
