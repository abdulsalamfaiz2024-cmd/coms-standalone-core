
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def implement_phase_4a():
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()

    print("Implementing Phase 4A: Deliverable Doctype...")

    # 1. Deliverable Revision (Child Table)
    if not frappe.db.exists("DocType", "Deliverable Revision"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Deliverable Revision",
            "module": "Custom",
            "istable": 1,
            "custom": 1,
            "fields": [
                {"fieldname": "version_number", "fieldtype": "Int", "label": "Version Number", "read_only": 1, "in_list_view": 1},
                {"fieldname": "submitted_by", "fieldtype": "Link", "label": "Submitted By", "options": "User", "read_only": 1, "in_list_view": 1},
                {"fieldname": "submission_date", "fieldtype": "Datetime", "label": "Submission Date", "read_only": 1, "in_list_view": 1},
                {"fieldname": "file", "fieldtype": "Attach", "label": "File", "reqd": 1, "in_list_view": 1},
                {"fieldname": "comments", "fieldtype": "Small Text", "label": "Comments"}
            ]
        })
        doc.insert()
        print("✓ DocType 'Deliverable Revision' created")
    else:
        print("- DocType 'Deliverable Revision' already exists")

    # 2. Deliverable (Main DocType)
    if not frappe.db.exists("DocType", "Deliverable"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Deliverable",
            "module": "Custom",
            "custom": 1,
            "autoname": "naming_series:",
            "is_submittable": 1,
            "track_changes": 1,
            "fields": [
                {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "DEL-.YYYY.-.#####", "default": "DEL-.YYYY.-.#####", "reqd": 1, "hidden": 0},
                {"fieldname": "deliverable_name", "fieldtype": "Data", "label": "Deliverable Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "project", "fieldtype": "Link", "label": "Project", "options": "Project", "reqd": 1, "in_list_view": 1},
                
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nIn Progress\nSubmitted\nUnder Review\nApproved\nRevision Required\nFinal\nCancelled", "default": "Draft", "in_list_view": 1},
                
                {"fieldname": "deliverable_type", "fieldtype": "Select", "label": "Deliverable Type", "options": "Report\nPresentation\nDataset\nTool/Application\nDocumentation\nTraining Material\nFinancial Statement\nOther", "in_list_view": 1},
                {"fieldname": "priority", "fieldtype": "Select", "label": "Priority", "options": "Low\nMedium\nHigh\nCritical", "default": "Medium", "in_list_view": 1},
                
                {"fieldname": "due_date", "fieldtype": "Date", "label": "Due Date", "reqd": 1, "in_list_view": 1},
                {"fieldname": "submission_date", "fieldtype": "Date", "label": "Submission Date", "read_only": 1},
                
                {"fieldname": "task", "fieldtype": "Link", "label": "Linked Task", "options": "Task"},
                {"fieldname": "assigned_consultant", "fieldtype": "Link", "label": "Assigned Consultant", "options": "Employee"},
                {"fieldname": "approver", "fieldtype": "Link", "label": "Approver", "options": "User"},
                
                {"fieldname": "sb_details", "fieldtype": "Section Break", "label": "Details"},
                {"fieldname": "description", "fieldtype": "Text Editor", "label": "Description"},
                
                {"fieldname": "sb_revisions", "fieldtype": "Section Break", "label": "Revisions"},
                {"fieldname": "current_version", "fieldtype": "Int", "label": "Current Version", "read_only": 1, "default": 0},
                {"fieldname": "revisions", "fieldtype": "Table", "label": "Revisions", "options": "Deliverable Revision"},
                
                {"fieldname": "sb_approval", "fieldtype": "Section Break", "label": "Approval"},
                {"fieldname": "approval_status", "fieldtype": "Select", "label": "Approval Status", "options": "Pending\nApproved\nRejected", "default": "Pending"},
                {"fieldname": "approved_by", "fieldtype": "Link", "label": "Approved By", "options": "User", "read_only": 1},
                {"fieldname": "approved_on", "fieldtype": "Datetime", "label": "Approved On", "read_only": 1},
                {"fieldname": "rejection_reason", "fieldtype": "Small Text", "label": "Rejection Reason", "read_only": 1},
                
                {"fieldname": "sb_context", "fieldtype": "Section Break", "label": "Context", "collapsible": 1},
                {"fieldname": "client_contract", "fieldtype": "Link", "label": "Client Contract", "options": "Client Contract", "read_only": 1},
                {"fieldname": "customer", "fieldtype": "Link", "label": "Customer", "options": "Customer", "read_only": 1},
            ],
            "permissions": [
                {"role": "System Manager", "read":1, "write":1, "create":1, "delete":1, "submit": 1, "cancel": 1},
                {"role": "Projects User", "read":1, "write":1, "create":1},
                {"role": "Projects Manager", "read":1, "write":1, "create":1, "delete":1, "submit": 1, "cancel": 1}
            ]
        })
        doc.insert()
        print("✓ DocType 'Deliverable' created")
    else:
        print("- DocType 'Deliverable' already exists")

    # 3. Custom Field on Task
    create_custom_fields({
        "Task": [
            {
                "label": "Deliverable",
                "fieldname": "deliverable",
                "fieldtype": "Link",
                "options": "Deliverable",
                "insert_after": "project",
                "description": "Linked deliverable for this task"
            }
        ]
    })
    print("✓ Custom Field Task.deliverable created")

    frappe.db.commit()

implement_phase_4a()
