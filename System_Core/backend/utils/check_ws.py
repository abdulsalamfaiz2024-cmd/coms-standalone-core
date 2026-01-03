
import frappe

def check_workspace():
    result = frappe.db.sql("SELECT name, label, module FROM tabWorkspace WHERE module='Consulting' OR name='Consulting'", as_dict=True)
    print("Workspaces found:", result)
    
    # Also list all workspaces
    all_ws = frappe.db.sql("SELECT name, label, module FROM tabWorkspace", as_dict=True)
    print("All workspaces:", [w['name'] for w in all_ws])

check_workspace()
