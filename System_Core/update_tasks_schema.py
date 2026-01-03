
import sqlite3
import os

DB_PATH = r'd:\Custom_System_Copy\System_Core\consultancy.db'

def update_schema():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Dropping old Tasks table...")
    cursor.execute("DROP TABLE IF EXISTS Tasks")

    print("Creating new Tasks table...")
    cursor.execute("""
    CREATE TABLE "Tasks" (
        "id" TEXT PRIMARY KEY,
        "Assignment" TEXT,
        "Consultant" TEXT,
        "Title" TEXT,
        "DueDate" TEXT,
        "Contract_Ref" TEXT,
        "StartDate" TEXT,
        "EndDate" TEXT,
        "TaskDetails" TEXT,
        "Sessions" TEXT,
        "Hours" TEXT,
        "Days" TEXT,
        "Status" TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("Tasks table updated successfully.")

if __name__ == "__main__":
    update_schema()
