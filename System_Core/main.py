
import sys
import os

# Ensure local system modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import run_server

print("=========================================")
print("   CONSULTANCY OS RELATIONAL v2.0        ")
print("=========================================")
print("Core: Independent Relational Engine")
print("Database: consultancy.db (SQLite)")

if __name__ == "__main__":
    # Check if DB exists, if not, offer hint
    db_path = os.path.join(os.path.dirname(__file__), "consultancy.db")
    if not os.path.exists(db_path):
        print(f"WARNING: Database not found at {db_path}")
        print("Please run 'create_relational_db.py' first.")
    
    run_server()
