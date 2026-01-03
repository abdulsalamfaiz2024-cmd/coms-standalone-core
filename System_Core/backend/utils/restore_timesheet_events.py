# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def on_timesheet_validate(doc, method):
    """Validate timesheet and set rates"""
    fetch_consultant_contract(doc)
    set_consultant_rates(doc)
    validate_project_contract(doc)

def fetch_consultant_contract(doc):
    """Fetch active consultant contract"""
    if doc.employee:
        contract = frappe.db.get_value(
            "Consultant Contract",
            {
                "consultant": doc.employee,
                "status": "Active"
            },
            ["name", "rate_type", "rate_amount"],
            as_dict=True
        )
        
        if contract:
            doc.consultant_contract = contract.name
            doc.contract_rate_type = contract.rate_type

def set_consultant_rates(doc):
    """
    Set billing rates based on rate hierarchy:
    1. Override rate (consultant_rate in detail) - highest priority
    2. Contract rate (from Consultant Contract)
    3. Employee default rate (hourly_rate on Employee)
    """
    if not doc.employee:
        return
    
    # Get contract details
    contract = None
    if doc.consultant_contract:
        contract = frappe.get_doc("Consultant Contract", doc.consultant_contract)
    
    # Get employee default rate
    employee = frappe.get_doc("Employee", doc.employee)
    default_rate = flt(employee.hourly_rate)
    
    for row in doc.time_logs:
        # Determine which rate to use
        if row.consultant_rate:
            # Override rate specified
            rate = flt(row.consultant_rate)
            row.rate_source = "Override"
        elif contract:
            # Use contract rate
            if contract.rate_type == "Hourly":
                rate = flt(contract.rate_amount)
            elif contract.rate_type == "Daily":
                # Convert daily to hourly (assuming 8-hour day)
                rate = flt(contract.rate_amount) / 8
            elif contract.rate_type == "Monthly":
                # Convert monthly to hourly (assuming 160 hours/month)
                rate = flt(contract.rate_amount) / 160
            else:
                rate = flt(contract.rate_amount)
            
            row.contract_rate = contract.rate_amount
            row.rate_source = "Contract"
        else:
            # Use employee default rate
            rate = default_rate
            row.rate_source = "Default"
        
        # Set billing rate and amount if billable
        # Standard field is 'is_billable'
        if row.is_billable:
            row.billing_rate = rate
            row.billing_amount = flt(row.billing_hours or row.hours) * rate
        else:
            row.billing_amount = 0.0
            
        # Always set costing rate
        row.costing_rate = rate
        # row.costing_amount = flt(row.hours) * rate (Calculated by system usually, but we set it to be sure)
        # Actually standard timesheet calculates costing_amount. We just set rate.

def validate_project_contract(doc):
    """Fetch client contract from project"""
    for row in doc.time_logs:
        if row.project:
            client_contract = frappe.db.get_value(
                "Project",
                row.project,
                "client_contract"
            )
            if client_contract:
                row.client_contract = client_contract

def on_timesheet_submit(doc, method):
    """Actions when timesheet is submitted"""
    # Standard ERPNext updates Task.actual_time, so we only update our custom table
    update_project_consultant_hours(doc)

def on_timesheet_cancel(doc, method):
    """Revert actions when timesheet is cancelled"""
    # Standard ERPNext reverts Task.actual_time
    update_project_consultant_hours(doc, revert=True)

def update_project_consultant_hours(doc, revert=False):
    """Update actual hours in project consultant team"""
    multiplier = -1 if revert else 1
    
    # Group hours by project
    project_hours = {}
    for row in doc.time_logs:
        if row.project:
            if row.project not in project_hours:
                project_hours[row.project] = 0
            # Use row.hours which is standard
            project_hours[row.project] += flt(row.hours)
    
    # Update each project
    for project_name, hours in project_hours.items():
        try:
            project = frappe.get_doc("Project", project_name)
            
            updated = False
            for consultant in project.get("consultant_team", []):
                if consultant.consultant == doc.employee:
                    consultant.actual_hours = max(
                        0,
                        flt(consultant.actual_hours) + (hours * multiplier)
                    )
                    updated = True
            
            if updated:
                project.flags.ignore_validate = True
                project.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(
                f"Error updating project hours: {str(e)}",
                "Timesheet Hours Update"
            )
