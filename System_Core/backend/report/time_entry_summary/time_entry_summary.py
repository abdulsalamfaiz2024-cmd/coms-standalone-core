# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "project", "label": _("Project"), "fieldtype": "Link",
         "options": "Project", "width": 180},
        {"fieldname": "task", "label": _("Task"), "fieldtype": "Link",
         "options": "Task", "width": 180},
        {"fieldname": "employee", "label": _("Consultant"), "fieldtype": "Link",
         "options": "Employee", "width": 150},
        {"fieldname": "employee_name", "label": _("Name"), "fieldtype": "Data", "width": 120},
        {"fieldname": "activity_type", "label": _("Activity"), "fieldtype": "Data", "width": 100},
        {"fieldname": "hours", "label": _("Hours"), "fieldtype": "Float", "width": 80},
        {"fieldname": "billing_hours", "label": _("Billable Hrs"), "fieldtype": "Float", "width": 100},
        {"fieldname": "billing_amount", "label": _("Amount"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "billed", "label": _("Invoiced"), "fieldtype": "Check", "width": 80}
    ]


def get_data(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += f" AND td.from_time >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND td.to_time <= '{filters.get('to_date')}'"
    if filters.get("project"):
        conditions += f" AND td.project = '{filters.get('project')}'"
    if filters.get("employee"):
        conditions += f" AND ts.employee = '{filters.get('employee')}'"
    
    data = frappe.db.sql(f"""
        SELECT 
            td.project,
            td.task,
            ts.employee,
            ts.employee_name,
            td.activity_type,
            td.hours,
            td.billing_hours,
            td.billing_amount,
            CASE WHEN td.sales_invoice IS NOT NULL THEN 1 ELSE 0 END as billed
        FROM `tabTimesheet Detail` td
        INNER JOIN `tabTimesheet` ts ON ts.name = td.parent
        WHERE ts.docstatus = 1
        {conditions}
        ORDER BY td.from_time DESC
        LIMIT 500
    """, as_dict=True)
    
    return data


def get_chart(data):
    if not data:
        return None
        
    # Group by project
    project_hours = {}
    for row in data:
        project = row.get("project") or "No Project"
        if project not in project_hours:
            project_hours[project] = 0
        project_hours[project] += flt(row.get("hours", 0))
    
    sorted_projects = sorted(project_hours.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "data": {
            "labels": [p[0] for p in sorted_projects],
            "datasets": [{"name": _("Hours"), "values": [p[1] for p in sorted_projects]}]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }
