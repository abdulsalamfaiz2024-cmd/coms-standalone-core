# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "contract", "label": _("Contract"), "fieldtype": "Link",
         "options": "Client Contract", "width": 150},
        {"fieldname": "contract_title", "label": _("Title"), "fieldtype": "Data", "width": 200},
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link",
         "options": "Customer", "width": 150},
        {"fieldname": "contract_value", "label": _("Value"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_milestones", "label": _("Milestones"), "fieldtype": "Int", "width": 80},
        {"fieldname": "completed_milestones", "label": _("Completed"), "fieldtype": "Int", "width": 80},
        {"fieldname": "milestone_compliance", "label": _("Compliance %"), "fieldtype": "Percent", "width": 100},
        {"fieldname": "invoiced_amount", "label": _("Invoiced"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "invoice_compliance", "label": _("Invoiced %"), "fieldtype": "Percent", "width": 100}
    ]


def get_data(filters):
    filter_conditions = {"status": ["in", ["Active", "Completed"]]}
    
    if filters.get("customer"):
        filter_conditions["client"] = filters.get("customer")
    if filters.get("status"):
        filter_conditions["status"] = filters.get("status")
    
    contracts = frappe.get_all(
        "Client Contract",
        filters=filter_conditions,
        fields=["name", "contract_title", "client", "contract_value", "invoiced_amount"]
    )
    
    data = []
    for contract in contracts:
        # Get milestone stats
        milestones = frappe.get_all(
            "Contract Milestone",
            filters={"parent": contract.name},
            fields=["status"]
        )
        
        total = len(milestones)
        completed = len([m for m in milestones if m.status in ["Completed", "Invoiced"]])
        
        milestone_compliance = (completed / total * 100) if total else 0
        invoice_compliance = (flt(contract.invoiced_amount) / flt(contract.contract_value) * 100) \
                             if contract.contract_value else 0
        
        data.append({
            "contract": contract.name,
            "contract_title": contract.contract_title,
            "customer": contract.client,
            "contract_value": contract.contract_value,
            "total_milestones": total,
            "completed_milestones": completed,
            "milestone_compliance": round(milestone_compliance, 1),
            "invoiced_amount": contract.invoiced_amount,
            "invoice_compliance": round(invoice_compliance, 1)
        })
    
    return data
