
import frappe

def fix_workspace():
    frappe.db.set_value('Workspace', 'Consulting', 'public', 1)
    frappe.db.commit()
    print("Workspace set to public")

fix_workspace()
