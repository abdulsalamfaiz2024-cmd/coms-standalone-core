import sqlite3
import hashlib

conn = sqlite3.connect('System_Core/consultancy.db')
cursor = conn.cursor()

# Get all users with potentially unhashed passwords (hash < 64 chars)
cursor.execute('SELECT id, username, password_hash FROM Users WHERE LENGTH(password_hash) < 64')
bad_users = cursor.fetchall()

if bad_users:
    print('Fixing users with plain-text passwords:')
    # Reset their passwords to 'password123' (hashed)
    default_hash = hashlib.sha256('password123'.encode()).hexdigest()
    for user in bad_users:
        print(f'  - {user[1]}: resetting password to "password123"')
        cursor.execute('UPDATE Users SET password_hash = ? WHERE id = ?', (default_hash, user[0]))
    conn.commit()
    print('')
    print('Done! All users now have properly hashed passwords.')
    print('Default password for reset users: password123')
else:
    print('All passwords are already properly hashed.')

conn.close()
