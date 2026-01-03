
import sqlite3
import json
import os

DB_FILE = "d:/Custom_System_Copy/System_Core/consultancy.db"
DOCTYPE_DIR = "d:/Custom_System_Copy/System_Core/backend/doctype"

def get_sql_type(fieldtype):
    if fieldtype == "Currency": return "REAL"
    if fieldtype == "Date": return "TEXT"
    if fieldtype == "Long Text": return "TEXT"
    return "TEXT"

def generate_schema():
    sql_statements = []
    
    doctypes = [d for d in os.listdir(DOCTYPE_DIR) if os.path.isdir(os.path.join(DOCTYPE_DIR, d))]
    
    for dt in doctypes:
        json_path = os.path.join(DOCTYPE_DIR, dt, f"{dt}.json")
        if not os.path.exists(json_path): continue
        
        with open(json_path, 'r') as f:
            meta = json.load(f)
            
        table_name = meta['name']
        fields = meta['fields']
        
        cols = ['"id" TEXT PRIMARY KEY']
        for f in fields:
            col_name = f['fieldname']
            col_type = get_sql_type(f['fieldtype'])
            cols.append(f'"{col_name}" {col_type}')
            
        create_stmt = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    ' + ",\n    ".join(cols) + "\n);"
        sql_statements.append(create_stmt)
        
    return sql_statements

def main():
    statements = generate_schema()
    
    with open("d:/Custom_System_Copy/System_Core/schema.sql", "w") as f:
        f.write("\n\n".join(statements))
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for stmt in statements:
        cursor.execute(stmt)
    conn.commit()
    conn.close()
    print(f"Database created at {DB_FILE} with independent tables.")

if __name__ == "__main__":
    main()
