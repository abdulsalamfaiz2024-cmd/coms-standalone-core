
import sqlite3
import json

OLD_DB = "d:/Custom_System_Copy/System_Core/system.db"
NEW_DB = "d:/Custom_System_Copy/System_Core/consultancy.db"

def migrate():
    if not os.path.exists(OLD_DB):
        print("No old data found.")
        return
        
    conn_old = sqlite3.connect(OLD_DB)
    curr_old = conn_old.cursor()
    
    # Get all unique doctypes in old DB
    curr_old.execute("SELECT DISTINCT doctype FROM docs")
    doctypes = [r[0] for r in curr_old.fetchall()]
    print(f"Old doctypes: {doctypes}")
    
    conn_new = sqlite3.connect(NEW_DB)
    curr_new = conn_new.cursor()
    
    # Get all tables in new DB
    curr_new.execute('SELECT name FROM sqlite_master WHERE type="table"')
    new_tables = [t[0] for t in curr_new.fetchall()]
    new_tables_lower = {t.lower(): t for t in new_tables}

    for dt in doctypes:
        # Find matching table
        target_table = new_tables_lower.get(dt.lower())
        if not target_table:
            print(f"No match for {dt}")
            continue
            
        print(f"Migrating {dt} -> {target_table}")
        
        curr_old.execute("SELECT json FROM docs WHERE doctype = ?", (dt,))
        rows = curr_old.fetchall()
        
        curr_new.execute(f'PRAGMA table_info("{target_table}")')
        cols = [r[1] for r in curr_new.fetchall()]
        
        for (json_str,) in rows:
            data = json.loads(json_str)
            doc_id = data.get('id') or data.get('name')
            data['id'] = doc_id
            
            filtered_data = {k: v for k, v in data.items() if k in cols}
            keys = list(filtered_data.keys())
            values = list(filtered_data.values())
            
            placeholders = ", ".join(["?"] * len(keys))
            cols_str = ", ".join([f'"{k}"' for k in keys])
            
            query = f'INSERT OR REPLACE INTO "{target_table}" ({cols_str}) VALUES ({placeholders})'
            try:
                curr_new.execute(query, values)
            except Exception as e:
                print(f"Error migrating row in {dt}: {e}")
                
    conn_new.commit()
    conn_old.close()
    conn_new.close()
    print("Migration complete.")

import os
if __name__ == "__main__":
    migrate()
