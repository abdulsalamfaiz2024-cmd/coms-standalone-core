
import sqlite3
conn = sqlite3.connect('d:/Custom_System_Copy/System_Core/consultancy.db')
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [t[0] for t in c.fetchall()]
print(f"Total tables: {len(tables)}")
for t in tables[:10]:
    c.execute(f'SELECT count(*) FROM "{t}"')
    count = c.fetchone()[0]
    print(f"Table '{t}': {count} records")
conn.close()
