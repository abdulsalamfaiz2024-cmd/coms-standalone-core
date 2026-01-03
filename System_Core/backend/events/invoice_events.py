# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


def update_contract_invoiced(doc, method):
    """Update contract invoiced amount when Sales Invoice is submitted"""
    contract_name = None
    
    # Get contract from invoice directly (Phase 5A field)
    if hasattr(doc, 'client_contract') and doc.client_contract:
        contract_name = doc.client_contract
    # Or from project
    elif doc.project:
        contract_name = frappe.db.get_value("Project", doc.project, "client_contract")
    # Or from invoice items
    else:
        for item in doc.items:
            if item.project:
                contract = frappe.db.get_value("Project", item.project, "client_contract")
                if contract:
                    contract_name = contract
                    break
    
    if contract_name:
        update_contract_amounts(contract_name)


def revert_contract_invoiced(doc, method):
    """Revert contract invoiced amount when Sales Invoice is cancelled"""
    contract_name = None
    
    if hasattr(doc, 'client_contract') and doc.client_contract:
        contract_name = doc.client_contract
    elif doc.project:
        contract_name = frappe.db.get_value("Project", doc.project, "client_contract")
    else:
        for item in doc.items:
            if item.project:
                contract = frappe.db.get_value("Project", item.project, "client_contract")
                if contract:
                    contract_name = contract
                    break
    
    if contract_name:
        update_contract_amounts(contract_name)


def update_contract_amounts(contract_name):
    """Recalculate contract invoiced and paid amounts"""
    try:
        contract = frappe.get_doc("Client Contract", contract_name)
        
        # Get all invoices linked to this contract or its projects
        project_names = [p.project for p in contract.get("projects", [])]
        
        # Invoices directly linked to contract
        invoiced_direct = frappe.db.sql("""
            SELECT COALESCE(SUM(grand_total), 0) as total
            FROM `tabSales Invoice`
            WHERE client_contract = %s
            AND docstatus = 1
        """, (contract_name,), as_dict=True)
        
        invoiced = flt(invoiced_direct[0].total) if invoiced_direct else 0
        
        # Invoices linked via projects
        if project_names:
            invoiced_project = frappe.db.sql("""
                SELECT COALESCE(SUM(grand_total), 0) as total
                FROM `tabSales Invoice`
                WHERE project IN %s
                AND (client_contract IS NULL OR client_contract = '')
                AND docstatus = 1
            """, (tuple(project_names),), as_dict=True)
            
            invoiced += flt(invoiced_project[0].total) if invoiced_project else 0
        
        # Get paid amounts from Payment Entries
        paid = get_contract_paid_amount(contract_name, project_names)
        
        # Update contract fields
        contract.db_set("invoiced_amount", invoiced, update_modified=False)
        
        # Only update if field exists
        if frappe.db.has_column("Client Contract", "paid_amount"):
            contract.db_set("paid_amount", paid, update_modified=False)
        
        if frappe.db.has_column("Client Contract", "outstanding_amount"):
            contract.db_set("outstanding_amount", invoiced - paid, update_modified=False)
            
    except Exception as e:
        frappe.log_error(
            f"Error updating contract amounts for {contract_name}: {str(e)}",
            "Contract Amount Update"
        )


def get_contract_paid_amount(contract_name, project_names):
    """Calculate total paid amount for contract"""
    paid = 0
    
    try:
        # Build filter for invoices
        conditions = [f"si.client_contract = '{contract_name}'"]
        
        if project_names:
            projects_str = "', '".join(project_names)
            conditions.append(f"si.project IN ('{projects_str}')")
        
        where_clause = " OR ".join(conditions)
        
        result = frappe.db.sql(f"""
            SELECT COALESCE(SUM(per.allocated_amount), 0) as total
            FROM `tabPayment Entry Reference` per
            INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
            INNER JOIN `tabSales Invoice` si ON si.name = per.reference_name
            WHERE ({where_clause})
            AND pe.docstatus = 1
            AND per.reference_doctype = 'Sales Invoice'
        """, as_dict=True)
        
        paid = flt(result[0].total) if result else 0
        
    except Exception as e:
        frappe.log_error(
            f"Error calculating paid amount for {contract_name}: {str(e)}",
            "Contract Paid Amount"
        )
    
    return paid
