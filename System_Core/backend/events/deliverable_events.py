# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, today, add_days


def on_deliverable_validate(doc, method):
    """Validate deliverable"""
    sync_status_with_workflow(doc)
    check_overdue(doc)


def sync_status_with_workflow(doc):
    """Sync status field with workflow state"""
    if doc.workflow_state:
        doc.status = doc.workflow_state


def check_overdue(doc):
    """Check if deliverable is overdue"""
    if doc.due_date and doc.status not in ["Final", "Cancelled", "Approved"]:
        if getdate(doc.due_date) < getdate(today()):
            frappe.msgprint(
                _("This deliverable is overdue. Due date was {0}").format(
                    frappe.format_date(doc.due_date)
                ),
                indicator="red",
                alert=True
            )


def on_deliverable_update(doc, method):
    """Actions after deliverable update"""
    update_task_deliverable_link(doc)


def update_task_deliverable_link(doc):
    """Update task with deliverable link"""
    if doc.task:
        frappe.db.set_value(
            "Task",
            doc.task,
            "deliverable",
            doc.name,
            update_modified=False
        )


def send_overdue_alerts():
    """
    Scheduled task to send alerts for overdue deliverables.
    Add to scheduler_events in hooks.py
    """
    overdue_deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "status": ["not in", ["Final", "Cancelled", "Approved"]],
            "due_date": ["<", today()],
            "docstatus": ["!=", 2]
        },
        fields=["name", "deliverable_name", "project", "assigned_consultant", "due_date"]
    )
    
    for deliverable in overdue_deliverables:
        if deliverable.assigned_consultant:
            user_id = frappe.db.get_value(
                "Employee",
                deliverable.assigned_consultant,
                "user_id"
            )
            
            if user_id:
                frappe.publish_realtime(
                    event="deliverable_overdue",
                    message={
                        "deliverable": deliverable.name,
                        "deliverable_name": deliverable.deliverable_name,
                        "project": deliverable.project,
                        "due_date": str(deliverable.due_date)
                    },
                    user=user_id
                )


def get_due_soon_deliverables():
    """Get deliverables due in the next 3 days"""
    today_date = getdate(today())
    three_days_later = add_days(today_date, 3)
    
    return frappe.get_all(
        "Deliverable",
        filters={
            "status": ["not in", ["Final", "Cancelled", "Approved"]],
            "due_date": ["between", [today_date, three_days_later]],
            "docstatus": ["!=", 2]
        },
        fields=["name", "deliverable_name", "project", "due_date", "assigned_consultant"]
    )
