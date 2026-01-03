# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, today, flt


def validate_task(doc, method):
    """Validate task document"""
    validate_consultant_availability(doc)
    fetch_consultant_contract(doc)


def validate_consultant_availability(doc):
    """Check if consultant is over-allocated for task dates"""
    if not doc.assigned_consultant or not doc.exp_start_date:
        return
    
    # Get consultant's current allocation across active projects
    start_date = doc.exp_start_date
    end_date = doc.exp_end_date or doc.exp_start_date
    
    allocation = frappe.db.sql("""
        SELECT 
            SUM(pc.allocation_percentage) as total_allocation,
            GROUP_CONCAT(p.project_name) as projects
        FROM `tabProject Consultant` pc
        INNER JOIN `tabProject` p ON p.name = pc.parent
        WHERE pc.consultant = %s
        AND p.status = 'Open'
        AND p.name != %s
        AND (
            (p.expected_start_date <= %s AND 
             (p.expected_end_date >= %s OR p.expected_end_date IS NULL))
        )
    """, (doc.assigned_consultant, doc.project or "", end_date, start_date), 
         as_dict=True)
    
    if allocation and allocation[0].total_allocation:
        total = flt(allocation[0].total_allocation)
        if total >= 100:
            frappe.msgprint(
                _("Warning: {0} is already at {1}% allocation on: {2}").format(
                    doc.assigned_consultant,
                    total,
                    allocation[0].projects
                ),
                indicator="orange",
                alert=True
            )


def fetch_consultant_contract(doc):
    """Fetch active contract for assigned consultant"""
    if doc.assigned_consultant:
        contract = frappe.db.get_value(
            "Consultant Contract",
            {
                "consultant": doc.assigned_consultant,
                "status": "Active"
            },
            "name"
        )
        if contract:
            doc.consultant_contract = contract


def on_task_update(doc, method):
    """Actions after task is saved"""
    add_consultant_to_project_team(doc)
    sync_frappe_assignment(doc)


def add_consultant_to_project_team(doc):
    """Add assigned consultant to project's consultant team"""
    if not doc.project or not doc.assigned_consultant:
        return
    
    project = frappe.get_doc("Project", doc.project)
    
    # Check if consultant already in team
    existing_consultants = [c.consultant for c in project.get("consultant_team", [])]
    
    if doc.assigned_consultant not in existing_consultants:
        # Get consultant's hourly rate
        hourly_rate = frappe.db.get_value(
            "Employee",
            doc.assigned_consultant,
            "hourly_rate"
        ) or 0
        
        project.append("consultant_team", {
            "consultant": doc.assigned_consultant,
            "role": "Task Assignee",
            "allocation_percentage": 100,
            "hourly_rate": hourly_rate,
            "start_date": doc.exp_start_date,
            "end_date": doc.exp_end_date
        })
        
        project.flags.ignore_validate = True
        project.save(ignore_permissions=True)
        
        frappe.msgprint(
            _("Added {0} to project team").format(doc.assigned_consultant),
            indicator="green",
            alert=True
        )


def sync_frappe_assignment(doc):
    """Sync with Frappe's ToDo assignment system"""
    if not doc.assigned_consultant:
        return
    
    # Get user_id for the employee
    user_id = frappe.db.get_value("Employee", doc.assigned_consultant, "user_id")
    
    if not user_id:
        return
    
    # Check if already assigned in Frappe
    existing_assignment = frappe.db.exists(
        "ToDo",
        {
            "reference_type": "Task",
            "reference_name": doc.name,
            "allocated_to": user_id,
            "status": ("!=", "Cancelled")
        }
    )
    
    if not existing_assignment:
        # Create assignment
        todo = frappe.new_doc("ToDo")
        todo.reference_type = "Task"
        todo.reference_name = doc.name
        todo.allocated_to = user_id
        todo.description = doc.subject
        todo.priority = doc.priority or "Medium"
        todo.date = doc.exp_end_date
        todo.insert(ignore_permissions=True)


def on_task_before_save(doc, method):
    """Before save hook"""
    # Update workflow state based on assignment
    if doc.assigned_consultant and doc.workflow_state == "Open":
        # Auto-transition to Assigned when consultant is set
        doc.workflow_state = "Assigned"


def update_task_actual_hours(task_name):
    """Update task's actual hours from timesheets"""
    hours = frappe.db.sql("""
        SELECT COALESCE(SUM(td.hours), 0) as total_hours
        FROM `tabTimesheet Detail` td
        INNER JOIN `tabTimesheet` ts ON ts.name = td.parent
        WHERE td.task = %s
        AND ts.docstatus = 1
    """, (task_name,), as_dict=True)
    
    if hours:
        frappe.db.set_value(
            "Task",
            task_name,
            "actual_time",
            hours[0].total_hours,
            update_modified=False
        )
