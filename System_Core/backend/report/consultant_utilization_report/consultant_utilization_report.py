# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    
    return columns, data, None, chart


def get_columns():
    return [
        {
            "fieldname": "employee",
            "label": _("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 180
        },
        {
            "fieldname": "employee_name",
            "label": _("Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
            "width": 120
        },
        {
            "fieldname": "consultant_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "available_hours",
            "label": _("Available Hours"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "billable_hours",
            "label": _("Billable Hours"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "non_billable_hours",
            "label": _("Non-Billable"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "total_hours",
            "label": _("Total Hours"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "utilization",
            "label": _("Utilization %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "billable_amount",
            "label": _("Billable Amount"),
            "fieldtype": "Currency",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    # Get all consultants (billable employees)
    consultants = frappe.db.sql("""
        SELECT 
            e.name as employee,
            e.employee_name,
            e.department,
            e.consultant_type,
            COALESCE(e.monthly_availability, 160) as available_hours
        FROM `tabEmployee` e
        WHERE e.status = 'Active'
        AND COALESCE(e.is_billable, 1) = 1
        {conditions}
        ORDER BY e.employee_name
    """.format(conditions=conditions.get("employee", "")), as_dict=True)
    
    # Get timesheet data for each consultant
    from_date = filters.get("from_date") or add_months(getdate(), -1)
    to_date = filters.get("to_date") or getdate()
    
    data = []
    
    for consultant in consultants:
        # Get hours from timesheets
        hours_data = frappe.db.sql("""
            SELECT 
                COALESCE(SUM(CASE WHEN td.billable = 1 THEN td.hours ELSE 0 END), 0) as billable_hours,
                COALESCE(SUM(CASE WHEN td.billable = 0 THEN td.hours ELSE 0 END), 0) as non_billable_hours,
                COALESCE(SUM(td.hours), 0) as total_hours,
                COALESCE(SUM(td.billing_amount), 0) as billable_amount
            FROM `tabTimesheet Detail` td
            INNER JOIN `tabTimesheet` ts ON ts.name = td.parent
            WHERE ts.employee = %s
            AND ts.docstatus = 1
            AND td.from_time >= %s
            AND td.to_time <= %s
        """, (consultant.employee, from_date, to_date), as_dict=True)
        
        hours = hours_data[0] if hours_data else {}
        
        billable = flt(hours.get("billable_hours", 0))
        non_billable = flt(hours.get("non_billable_hours", 0))
        total = flt(hours.get("total_hours", 0))
        available = flt(consultant.available_hours)
        
        # Calculate utilization (billable / available)
        utilization = (billable / available * 100) if available else 0
        
        data.append({
            "employee": consultant.employee,
            "employee_name": consultant.employee_name,
            "department": consultant.department,
            "consultant_type": consultant.consultant_type,
            "available_hours": available,
            "billable_hours": billable,
            "non_billable_hours": non_billable,
            "total_hours": total,
            "utilization": round(utilization, 1),
            "billable_amount": hours.get("billable_amount", 0)
        })
    
    return data


def get_conditions(filters):
    conditions = {}
    
    if filters.get("employee"):
        conditions["employee"] = f"AND e.name = '{filters.get('employee')}'"
    else:
        conditions["employee"] = ""
    
    if filters.get("department"):
        conditions["employee"] += f" AND e.department = '{filters.get('department')}'"
    
    return conditions


def get_chart(data):
    if not data:
        return None
    
    labels = [d["employee_name"] for d in data[:10]]  # Top 10
    billable = [d["billable_hours"] for d in data[:10]]
    non_billable = [d["non_billable_hours"] for d in data[:10]]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": _("Billable Hours"),
                    "values": billable
                },
                {
                    "name": _("Non-Billable Hours"),
                    "values": non_billable
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#ff5858"]
    }
