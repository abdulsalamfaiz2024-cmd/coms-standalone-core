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
        if row.is_billable: # Correct fieldname is 'is_billable' in Timesheet Detail? Check standard.
            # Standard Timesheet Detail has 'is_billable' (Check/Boolean)
            row.billing_rate = rate
            row.billing_amount = flt(row.billing_hours or row.hours) * rate
        
        # Always set costing rate
        row.costing_rate = rate
        # row.costing_amount = flt(row.hours) * rate # Standard ERPNext handles calculation if rate is set? 
        # Standard ERPNext calculates 'billing_amount' and 'costing_amount' in JS and Py controllers.
        # We should set rate and amount to be sure.
        row.costing_amount = flt(row.hours) * rate


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
    update_task_actual_hours(doc)
    update_project_consultant_hours(doc)


def on_timesheet_cancel(doc, method):
    """Revert actions when timesheet is cancelled"""
    update_task_actual_hours(doc, revert=True)
    update_project_consultant_hours(doc, revert=True)


def update_task_actual_hours(doc, revert=False):
    """Update actual hours on tasks"""
    multiplier = -1 if revert else 1
    
    for row in doc.time_logs:
        if row.task:
            current_hours = frappe.db.get_value("Task", row.task, "actual_time") or 0
            new_hours = flt(current_hours) + (flt(row.hours) * multiplier)
            
            frappe.db.set_value(
                "Task",
                row.task,
                "actual_time",
                max(0, new_hours),
                update_modified=False
            )


def update_project_consultant_hours(doc, revert=False):
    """Update actual hours in project consultant team"""
    multiplier = -1 if revert else 1
    
    # Group hours by project
    project_hours = {}
    for row in doc.time_logs:
        if row.project:
            if row.project not in project_hours:
                project_hours[row.project] = 0
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
