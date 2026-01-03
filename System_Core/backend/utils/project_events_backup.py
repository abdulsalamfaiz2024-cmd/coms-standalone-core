# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def validate_project(doc, method):
    """Validate project document"""
    validate_contract_link(doc)
    calculate_team_sizes(doc)


def validate_contract_link(doc):
    """Ensure project's contract belongs to same customer"""
    if doc.client_contract and doc.customer:
        contract_client = frappe.db.get_value(
            "Client Contract", 
            doc.client_contract, 
            "client"
        )
        if contract_client and contract_client != doc.customer:
            frappe.throw(
                _("Contract {0} belongs to {1}, not {2}").format(
                    doc.client_contract,
                    contract_client,
                    doc.customer
                )
            )


def calculate_team_sizes(doc):
    """Calculate internal and external team sizes"""
    internal_count = 0
    external_count = 0
    
    for consultant in doc.get("consultant_team", []):
        consultant_type = frappe.db.get_value(
            "Employee",
            consultant.consultant,
            "consultant_type"
        )
        if consultant_type == "Internal":
            internal_count += 1
        elif consultant_type in ["External", "Freelance"]:
            external_count += 1
    
    doc.internal_team_size = internal_count
    doc.external_team_size = external_count


def on_project_update(doc, method):
    """Actions after project is saved"""
    update_contract_projects(doc)
    update_billing_status(doc)


def update_contract_projects(doc):
    """Add project to contract's project list if linked"""
    if doc.client_contract:
        contract = frappe.get_doc("Client Contract", doc.client_contract)
        
        # Check if project already in list
        existing = [p.project for p in contract.projects]
        if doc.name not in existing:
            contract.append("projects", {
                "project": doc.name
            })
            contract.flags.ignore_validate = True
            contract.save(ignore_permissions=True)


def update_billing_status(doc):
    """Update billing status based on invoiced amount"""
    if not doc.client_contract:
        return
    
    contract = frappe.get_doc("Client Contract", doc.client_contract)
    invoiced = flt(contract.invoiced_amount)
    total = flt(contract.contract_value)
    
    if invoiced == 0:
        status = "Not Started"
    elif invoiced < total:
        status = "Partial"
    else:
        status = "Complete"
    
    if doc.billing_status != status:
        doc.db_set("billing_status", status, update_modified=False)


def update_consultant_actual_hours(project_name, employee, hours_delta):
    """Update consultant's actual hours in project team"""
    project = frappe.get_doc("Project", project_name)
    
    for consultant in project.consultant_team:
        if consultant.consultant == employee:
            consultant.actual_hours = flt(consultant.actual_hours) + flt(hours_delta)
    
    project.flags.ignore_validate = True
    project.save(ignore_permissions=True)
