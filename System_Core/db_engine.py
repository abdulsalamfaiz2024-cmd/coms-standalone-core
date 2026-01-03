
import sqlite3
import json
import uuid
from datetime import datetime

DB_PATH = "d:/Custom_System_Copy/System_Core/consultancy.db"

# --- AUDIT LOGGING SYSTEM ---

def log_audit(action, doctype, doc_id, changes=None, summary=None, user_id=None, username=None, ip_address=None):
    """
    Record an action in the AuditLog table.
    Actions: CREATE, UPDATE, DELETE, LOGIN, UPLOAD, etc.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        changes_json = json.dumps(changes) if changes else None
        
        cursor.execute('''
            INSERT INTO AuditLog (id, timestamp, user_id, username, action, doctype, doc_id, summary, changes, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (log_id, timestamp, user_id, username or 'System', action, doctype, doc_id, summary, changes_json, ip_address))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"AUDIT LOG ERROR: {e}")
        return False

def get_audit_log(doctype=None, doc_id=None, limit=50):
    """Retrieve audit logs, optionally filtered by doctype and doc_id."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if doctype and doc_id:
        cursor.execute('''
            SELECT * FROM AuditLog 
            WHERE doctype = ? AND doc_id = ? 
            ORDER BY timestamp DESC LIMIT ?
        ''', (doctype, doc_id, limit))
    elif doctype:
        cursor.execute('''
            SELECT * FROM AuditLog 
            WHERE doctype = ? 
            ORDER BY timestamp DESC LIMIT ?
        ''', (doctype, limit))
    else:
        cursor.execute('SELECT * FROM AuditLog ORDER BY timestamp DESC LIMIT ?', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def calculate_changes(old_data, new_data):
    """Compare old and new data, return dictionary of changes."""
    changes = {}
    all_keys = set(list(old_data.keys()) + list(new_data.keys()))
    
    for key in all_keys:
        if key in ['doctype', 'id']:  # Skip meta fields
            continue
        old_val = old_data.get(key, '')
        new_val = new_data.get(key, '')
        if str(old_val) != str(new_val):
            changes[key] = {'old': old_val, 'new': new_val}
    
    return changes if changes else None

# --- ROLE PERMISSIONS SYSTEM ---

def get_role_permissions(role):
    """Get permissions for a specific role."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT permissions FROM RolePermissions WHERE role = ?', (role,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None

def check_module_access(role, module):
    """Check if a role has access to a specific module."""
    perms = get_role_permissions(role)
    if not perms:
        return False
    
    # Admin has access to everything
    if '*' in perms.get('modules', []):
        return True
    
    # Check if module is in restricted list
    if module in perms.get('restricted_modules', []):
        return False
    
    # Check if module is in allowed list
    return module in perms.get('modules', [])

def check_action_permission(role, action):
    """Check if a role can perform a specific action (create, read, update, delete)."""
    perms = get_role_permissions(role)
    if not perms:
        return False
    return action in perms.get('actions', [])

def get_user_permissions(user_id):
    """Get full permission object for a user by their ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM Users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return get_role_permissions(row['role'])
    return None

def get_accessible_modules(role):
    """Get list of modules accessible to a role (for sidebar filtering)."""
    perms = get_role_permissions(role)
    if not perms:
        return []
    
    if '*' in perms.get('modules', []):
        # Return all modules for admin
        return ['*']
    
    return perms.get('modules', [])

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(query, params=(), fetchall=True):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetchall:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_all(table_name, search=None):
    if not table_name.isidentifier(): return []
    
    # --- AUTO-MAINTENANCE: Smart State Transition ---
    # Detect tables with 'Status' and 'EndDate' to auto-deactivate expired records
    try:
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d')
        # Check if table has the required columns for auto-transition
        check_conn = get_connection()
        info = check_conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
        cols = [r[1] for r in info]
        check_conn.close()
        
        if "Status" in cols and "EndDate" in cols:
            # Atomic update: Transition 'Active' to 'Inactive' if EndDate is in the past
            # Using a single SQL command for high performance
            auto_update_query = f'''
                UPDATE "{table_name}" 
                SET "Status" = 'Inactive' 
                WHERE "Status" = 'Active' 
                AND "EndDate" IS NOT NULL 
                AND "EndDate" != '' 
                AND "EndDate" < ?
            '''
            execute_query(auto_update_query, (now,), fetchall=False)
            print(f"DEBUG: Auto-Maintenance performed on '{table_name}' index.")
    except Exception as e:
        print(f"MAINTENANCE ERROR: {e}")

    query = f'SELECT * FROM "{table_name}"'
    params = ()
    
    if search:
        # Simple generic search across common fields or ID
        query += ' WHERE id LIKE ? OR "Title" LIKE ? OR "Consultants_name" LIKE ? OR "Client_Name" LIKE ?'
        search_val = f"%{search}%"
        params = (search_val, search_val, search_val, search_val)
    return execute_query(query, params)

def get_user_by_username(username):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_one(table_name, doc_id):
    if not table_name.isidentifier(): return None
    rows = execute_query(f'SELECT * FROM "{table_name}" WHERE id = ?', (doc_id,))
    return rows[0] if rows else None

def get_preview(table_name, doc_id):
    """Returns a subset of fields for a quick preview context."""
    doc = get_one(table_name, doc_id)
    if not doc: return None
    
    # Heuristic: Find name-like or title-like fields
    candidates = ['Title', 'Client_Name', 'Consultants_name', 'name', 'label', 'status', 'amount', 'date']
    preview = {k: v for k, v in doc.items() if k in candidates or k == 'id'}
    return preview

    return preview

def validate_business_logic(table_name, data):
    """
    Enforces server-side business rules before saving.
    Raises ValueError if data is invalid.
    """
    # Rule 1: Date Logic (EndDate must be >= StartDate)
    if 'StartDate' in data and 'EndDate' in data:
        start = data.get('StartDate')
        end = data.get('EndDate')
        if start and end and end < start:
            raise ValueError(f"End Date ({end}) cannot be before Start Date ({start})")

    # Rule 2: Numeric Sanity (No negative numbers for quantities)
    numeric_fields = ['Hours', 'Sessions', 'Days', 'Amount', 'TotalAmount']
    for field in numeric_fields:
        if field in data:
            try:
                val = float(data[field])
                if val < 0:
                    raise ValueError(f"{field} cannot be negative")
            except (ValueError, TypeError):
                pass # Ignore non-numeric inputs for now, or strict fail? Lenient for now.

    # Rule 3: Required Fields (Basic check if needed, though Schema usually handles this, we enforce criticals)
    if table_name == 'Users' and 'username' in data and len(data['username']) < 3:
         raise ValueError("Username must be at least 3 characters")

    return True

def save_one(table_name, data, user_id=None, username=None):
    """Save a record and log the action to AuditLog."""
    if not table_name.isidentifier(): return None
    
    # Skip audit logging for the AuditLog table itself
    skip_audit = table_name == 'AuditLog'
    
    # Run Validation
    validate_business_logic(table_name, data)
    
    # Determine if this is CREATE or UPDATE
    doc_id = data.get('id')
    is_new = False
    old_data = {}
    
    if not doc_id:
        doc_id = str(uuid.uuid4())
        data['id'] = doc_id
        is_new = True
    else:
        # Try to fetch existing record
        existing = get_one(table_name, doc_id)
        if existing:
            old_data = existing
        else:
            is_new = True
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    cols = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    filtered_data = {k: v for k, v in data.items() if k in cols}
    keys = list(filtered_data.keys())
    values = list(filtered_data.values())
    
    placeholders = ", ".join(["?"] * len(keys))
    cols_str = ", ".join([f'"{k}"' for k in keys])
    
    upsert_query = f'INSERT OR REPLACE INTO "{table_name}" ({cols_str}) VALUES ({placeholders})'
    execute_query(upsert_query, values, fetchall=False)
    
    # --- AUDIT LOGGING ---
    if not skip_audit:
        if is_new:
            # Log CREATE
            summary = f"Created new {table_name} record"
            log_audit(
                action='CREATE',
                doctype=table_name,
                doc_id=doc_id,
                changes=filtered_data,  # All fields as "new"
                summary=summary,
                user_id=user_id,
                username=username
            )
        else:
            # Log UPDATE with changes
            changes = calculate_changes(old_data, filtered_data)
            if changes:
                changed_fields = list(changes.keys())
                summary = f"Updated {len(changed_fields)} field(s): {', '.join(changed_fields)}"
                log_audit(
                    action='UPDATE',
                    doctype=table_name,
                    doc_id=doc_id,
                    changes=changes,
                    summary=summary,
                    user_id=user_id,
                    username=username
                )
    
    return doc_id

def delete_one(table_name, doc_id, user_id=None, username=None):
    """Delete a record and log the action to AuditLog."""
    if not table_name.isidentifier(): return False
    
    # Fetch the record BEFORE deleting (to log what was deleted)
    old_data = get_one(table_name, doc_id)
    
    query = f'DELETE FROM "{table_name}" WHERE id = ?'
    execute_query(query, (doc_id,), fetchall=False)
    
    # --- AUDIT LOGGING ---
    if old_data:
        # Get a readable name for the summary
        name_field = old_data.get('Title') or old_data.get('Client_Name') or old_data.get('Consultants_name') or old_data.get('name') or doc_id[:8]
        summary = f"Deleted {table_name}: {name_field}"
        log_audit(
            action='DELETE',
            doctype=table_name,
            doc_id=doc_id,
            changes=old_data,  # Store what was deleted
            summary=summary,
            user_id=user_id,
            username=username
        )
    
    return True

def save_file_record(file_data):
    # file_data: {id, file_name, file_path, parent_doctype, parent_id}
    keys = ['id', 'file_name', 'file_path', 'parent_doctype', 'parent_id']
    vals = [file_data.get(k) for k in keys]
    query = 'INSERT INTO Files (id, file_name, file_path, parent_doctype, parent_id) VALUES (?,?,?,?,?)'
    execute_query(query, vals, fetchall=False)
    return True

def get_files(parent_doctype, parent_id):
    query = 'SELECT * FROM Files WHERE parent_doctype = ? AND parent_id = ? ORDER BY uploaded_at DESC'
    return execute_query(query, (parent_doctype, parent_id))

# --- ADMIN / SETTINGS HELPERS ---

def get_settings():
    rows = execute_query("SELECT key, value FROM Settings")
    return {row['key']: row['value'] for row in rows}

def save_setting(key, value):
    execute_query("INSERT OR REPLACE INTO Settings (key, value) VALUES (?, ?)", (key, value), fetchall=False)

def get_users():
    return execute_query("SELECT id, username, role, full_name, email FROM Users") # Exclude password

def save_user(user_data):
    # user_data: {id, username, password (optional), role, full_name, email}
    import hashlib
    import uuid
    
    # Check if exists
    is_new = False
    if not user_data.get('id'):
        user_data['id'] = str(uuid.uuid4())
        is_new = True
    
    if is_new or user_data.get('password'):
        # Update with password
        if is_new and not user_data.get('password'): 
            raise ValueError("Password required for new user")
        
        # HASH the password using SHA-256 (matching server.py login verification)
        pwd_plain = user_data.get('password')
        pwd_hash = hashlib.sha256(pwd_plain.encode()).hexdigest()
        
        query = "INSERT OR REPLACE INTO Users (id, username, password_hash, role, full_name, email) VALUES (?, ?, ?, ?, ?, ?)"
        vals = (user_data['id'], user_data['username'], pwd_hash, user_data['role'], user_data['full_name'], user_data['email'])
    else:
        # Update without password
        query = "UPDATE Users SET username=?, role=?, full_name=?, email=? WHERE id=?"
        vals = (user_data['username'], user_data['role'], user_data['full_name'], user_data['email'], user_data['id'])
    
    execute_query(query, vals, fetchall=False)
    return True

def delete_user(user_id):
    if user_id == 'admin': return False # Protect main admin
    execute_query("DELETE FROM Users WHERE id = ?", (user_id,), fetchall=False)
    return True
