
import frappe

def create_project_fields():
    project_fields = [
        {
            "doctype": "Custom Field",
            "dt": "Project",
            "label": "Contract Value",
            "fieldname": "contract_value",
            "fieldtype": "Currency",
            "fetch_from": "client_contract.contract_value",
            "read_only": 1,
            "insert_after": "estimated_costing",
            "module": "Consulting",
            "description": "Automatically fetched from linked Client Contract"
        },
        {
            "doctype": "Custom Field",
            "dt": "Project",
            "label": "Billing Status",
            "fieldname": "billing_status",
            "fieldtype": "Select",
            "options": "Not Started\nPartial\nComplete",
            "default": "Not Started",
            "insert_after": "contract_value",
            "module": "Consulting"
        },
        {
            "doctype": "Custom Field",
            "dt": "Project",
            "label": "External Team Size",
            "fieldname": "external_team_size",
            "fieldtype": "Int",
            "read_only": 1,
            "insert_after": "users",
            "module": "Consulting",
            "description": "Count of external consultants on project"
        },
        {
            "doctype": "Custom Field",
            "dt": "Project",
            "label": "Internal Team Size",
            "fieldname": "internal_team_size",
            "fieldtype": "Int",
            "read_only": 1,
            "insert_after": "external_team_size",
            "module": "Consulting",
            "description": "Count of internal consultants on project"
        }
    ]

    for field in project_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            doc = frappe.get_doc(field)
            doc.insert()
            print(f"Created: {field['dt']}.{field['fieldname']}")
        else:
            print(f"Already exists: {field['dt']}.{field['fieldname']}")

    frappe.db.commit()
    print("Project custom fields created successfully!")

create_project_fields()
