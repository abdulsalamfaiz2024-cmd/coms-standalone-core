import sqlite3
import os

# Configuration
# BASE_DIR should be the root of the project
PROJECT_ROOT = "d:/Custom_System_Copy"
DB_PATH = os.path.join(PROJECT_ROOT, "System_Core", "consultancy.db")

SCHEMA_UPDATES = {
    "Consultancy_Assignments": [
        ("TotalContractValue", "REAL"),
        ("SignatoryName", "TEXT"),
        ("BillingContact", "TEXT"),
        ("PaymentTerms", "TEXT"),
        ("Objectives", "TEXT"),
        ("Scope_In", "TEXT"),
        ("Scope_Out", "TEXT"),
        ("Signed_Contract", "TEXT")
    ],
    "AssignmentConsultantRoles": [
        ("ContractType", "TEXT"),
        ("PaymentTrigger", "TEXT"),
        ("ExpensePolicy", "TEXT"),
        ("NDA_Signed", "INTEGER"),
        ("TerminationNotice", "TEXT"),
        ("Signed_Agreement", "TEXT")
    ],
    "Client_Invoices": [
        ("LineItems", "TEXT"),
        ("TaxID", "TEXT"),
        ("BankReference", "TEXT"),
        ("Terms", "TEXT"),
        ("PO_Number", "TEXT"),
        ("Invoice_File", "TEXT")
    ],
    "Consultant_Invoices": [
        ("LinkedTimesheets", "TEXT"),
        ("LinkedExpenses", "TEXT"),
        ("TaxAmount", "REAL"),
        ("Deductions", "REAL"),
        ("CleanTotal", "REAL"),
        ("Invoice_Upload", "TEXT")
    ],
    "Deliverables": [
        ("Version", "TEXT"),
        ("ReviewerID", "TEXT"),
        ("QualityMatrix", "TEXT"),
        ("RejectionReason", "TEXT"),
        ("Deliverable_File", "TEXT"),
        ("Internal_Comments", "TEXT")
    ]
}

def migrate():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for table, columns in SCHEMA_UPDATES.items():
        print(f"Checking table: {table}")
        
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table})")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        for col_name, col_type in columns:
            if col_name not in existing_cols:
                print(f"  -> Adding column: {col_name} ({col_type})")
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                except Exception as e:
                    print(f"     ERROR: {e}")
            else:
                print(f"  -> Column {col_name} already exists. Skipping.")
                
    conn.commit()
    conn.close()
    print("Migration Complete.")

if __name__ == "__main__":
    migrate()
