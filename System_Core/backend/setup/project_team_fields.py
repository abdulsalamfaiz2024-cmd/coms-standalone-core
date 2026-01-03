
import frappe

def create_consultant_team_field():
    field = {
        "doctype": "Custom Field",
        "dt": "Project",
        "label": "Consultant Team",
        "fieldname": "consultant_team",
        "fieldtype": "Table",
        "options": "Project Consultant",
        "insert_after": "users",
        "module": "Consulting",
        "description": "Consultants assigned to this project"
    }

    if not frappe.db.exists("Custom Field", {"dt": "Project", "fieldname": "consultant_team"}):
        doc = frappe.get_doc(field)
        doc.insert()
        print("Created Project.consultant_team table field")
    else:
        print("Field already exists")

    section = {
        "doctype": "Custom Field",
        "dt": "Project",
        "label": "Consulting Team",
        "fieldname": "consulting_team_section",
        "fieldtype": "Section Break",
        "insert_after": "users_section",
        "module": "Consulting",
        "collapsible": 1
    }

    if not frappe.db.exists("Custom Field", {"dt": "Project", "fieldname": "consulting_team_section"}):
        doc = frappe.get_doc(section)
        doc.insert()
        print("Created section break")

    frappe.db.commit()

create_consultant_team_field()
