# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, today


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "name", "label": _("Deliverable"), "fieldtype": "Link",
         "options": "Deliverable", "width": 120},
        {"fieldname": "deliverable_name", "label": _("Name"), "fieldtype": "Data", "width": 200},
        {"fieldname": "project", "label": _("Project"), "fieldtype": "Link",
         "options": "Project", "width": 150},
        {"fieldname": "deliverable_type", "label": _("Type"), "fieldtype": "Data", "width": 100},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "assigned_consultant", "label": _("Assigned To"), "fieldtype": "Link",
         "options": "Employee", "width": 120},
        {"fieldname": "due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "days_until_due", "label": _("Days Until Due"), "fieldtype": "Int", "width": 100},
        {"fieldname": "current_version", "label": _("Version"), "fieldtype": "Int", "width": 80}
    ]


def get_data(filters):
    conditions = ""
    if filters.get("project"):
        conditions += f" AND d.project = '{filters.get('project')}'"
    if filters.get("status"):
        conditions += f" AND d.status = '{filters.get('status')}'"
    
    data = frappe.db.sql(f"""
        SELECT 
            d.name,
            d.deliverable_name,
            d.project,
            d.deliverable_type,
            d.status,
            d.assigned_consultant,
            d.due_date,
            DATEDIFF(d.due_date, CURDATE()) as days_until_due,
            d.current_version
        FROM `tabDeliverable` d
        WHERE d.docstatus != 2
        {conditions}
        ORDER BY d.due_date ASC
    """, as_dict=True)
    
    return data
