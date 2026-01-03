# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, today


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link",
         "options": "Customer", "width": 200},
        {"fieldname": "total_invoiced", "label": _("Total Invoiced"), 
         "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_paid", "label": _("Total Paid"),
         "fieldtype": "Currency", "width": 120},
        {"fieldname": "outstanding", "label": _("Outstanding"),
         "fieldtype": "Currency", "width": 120},
        {"fieldname": "overdue", "label": _("Overdue Amount"),
         "fieldtype": "Currency", "width": 120},
        {"fieldname": "invoice_count", "label": _("Invoice Count"),
         "fieldtype": "Int", "width": 100},
        {"fieldname": "last_invoice_date", "label": _("Last Invoice"),
         "fieldtype": "Date", "width": 100}
    ]


def get_data(filters):
    conditions = ""
    if filters.get("customer"):
        conditions += f" AND si.customer = '{filters.get('customer')}'"
    if filters.get("from_date"):
        conditions += f" AND si.posting_date >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND si.posting_date <= '{filters.get('to_date')}'"
    
    # Check if is_consulting field exists
    is_consulting_filter = ""
    try:
        if frappe.db.has_column("Sales Invoice", "is_consulting"):
            is_consulting_filter = "AND si.is_consulting = 1"
    except Exception:
        pass
    
    data = frappe.db.sql(f"""
        SELECT 
            si.customer,
            SUM(si.grand_total) as total_invoiced,
            SUM(si.grand_total - si.outstanding_amount) as total_paid,
            SUM(si.outstanding_amount) as outstanding,
            SUM(CASE WHEN si.due_date < CURDATE() AND si.outstanding_amount > 0 
                THEN si.outstanding_amount ELSE 0 END) as overdue,
            COUNT(*) as invoice_count,
            MAX(si.posting_date) as last_invoice_date
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
        {is_consulting_filter}
        {conditions}
        GROUP BY si.customer
        ORDER BY outstanding DESC
    """, as_dict=True)
    
    return data
