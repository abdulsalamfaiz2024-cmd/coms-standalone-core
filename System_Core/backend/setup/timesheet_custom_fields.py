
import frappe

def create_timesheet_fields():
    # 1. Timesheet Header Fields
    timesheet_fields = [
        {
            "doctype": "Custom Field",
            "dt": "Timesheet",
            "label": "Consultant Contract",
            "fieldname": "consultant_contract",
            "fieldtype": "Link",
            "options": "Consultant Contract",
            "insert_after": "employee",
            "read_only": 1,
            "module": "Consulting",
            "description": "Active contract for this consultant"
        },
        {
            "doctype": "Custom Field",
            "dt": "Timesheet",
            "label": "Contract Rate Type",
            "fieldname": "contract_rate_type",
            "fieldtype": "Data",
            "insert_after": "consultant_contract",
            "read_only": 1,
            "module": "Consulting",
            "fetch_from": "consultant_contract.rate_type"
        }
    ]

    for field in timesheet_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            doc = frappe.get_doc(field)
            doc.insert()
            print(f"Created: {field['dt']}.{field['fieldname']}")
        else:
            print(f"Field {field['dt']}.{field['fieldname']} already exists")

    # 2. Timesheet Detail Fields
    detail_fields = [
        {
            "doctype": "Custom Field",
            "dt": "Timesheet Detail",
            "label": "Consultant Rate Override",
            "fieldname": "consultant_rate",
            "fieldtype": "Currency",
            "insert_after": "billing_rate",
            "module": "Consulting",
            "description": "Override rate for this entry (leave blank to use contract rate)"
        },
        {
            "doctype": "Custom Field",
            "dt": "Timesheet Detail",
            "label": "Contract Rate",
            "fieldname": "contract_rate",
            "fieldtype": "Currency",
            "insert_after": "consultant_rate",
            "read_only": 1,
            "module": "Consulting",
            "description": "Rate from consultant contract"
        },
        {
            "doctype": "Custom Field",
            "dt": "Timesheet Detail",
            "label": "Rate Source",
            "fieldname": "rate_source",
            "fieldtype": "Select",
            "options": "Default\nContract\nOverride",
            "insert_after": "contract_rate",
            "read_only": 1,
            "module": "Consulting"
        },
        {
            "doctype": "Custom Field",
            "dt": "Timesheet Detail",
            "label": "Client Contract",
            "fieldname": "client_contract",
            "fieldtype": "Link",
            "options": "Client Contract",
            "insert_after": "project",
            "read_only": 1,
            "module": "Consulting",
            "fetch_from": "project.client_contract"
        }
    ]

    for field in detail_fields:
        if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
            doc = frappe.get_doc(field)
            doc.insert()
            print(f"Created: {field['dt']}.{field['fieldname']}")
        else:
            print(f"Field {field['dt']}.{field['fieldname']} already exists")

    frappe.db.commit()

create_timesheet_fields()
