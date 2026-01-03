# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def generate_weekly_invoices():
    """
    Scheduled task to generate invoices weekly.
    Runs every Monday.
    Add to scheduler_events in hooks.py
    """
    from backend.billing.invoice_generator import ConsultingInvoiceGenerator
    
    generator = ConsultingInvoiceGenerator()
    invoices = generator.generate_all_pending_invoices()
    
    # Log results
    if invoices:
        frappe.log_error(
            f"Generated {len(invoices)} invoice(s): {', '.join(invoices)}",
            "Weekly Invoice Generation - Success"
        )
    
    if generator.errors:
        frappe.log_error(
            "\n".join(generator.errors),
            "Weekly Invoice Generation - Errors"
        )
    
    # Send notification to finance team
    if invoices:
        send_invoice_generation_notification(invoices)


def send_invoice_generation_notification(invoices):
    """Send notification about generated invoices"""
    # Get finance users
    finance_users = frappe.get_all(
        "Has Role",
        filters={"role": "Accounts User"},
        pluck="parent"
    )
    
    if not finance_users:
        return
    
    for user in finance_users[:5]:  # Limit to 5 users
        frappe.publish_realtime(
            event="invoices_generated",
            message={
                "count": len(invoices),
                "invoices": invoices[:10]  # First 10
            },
            user=user
        )


def remind_unbilled_time():
    """
    Send reminders about unbilled time entries.
    Runs daily.
    """
    from backend.billing.invoice_generator import get_unbilled_summary
    
    try:
        summary = get_unbilled_summary()
        
        if summary and summary.get("total_amount", 0) > 0:
            # Send to project managers
            managers = frappe.get_all(
                "Has Role",
                filters={"role": "Projects Manager"},
                pluck="parent"
            )
            
            for user in managers[:5]:
                frappe.publish_realtime(
                    event="unbilled_reminder",
                    message={
                        "total_hours": summary["total_hours"],
                        "total_amount": summary["total_amount"]
                    },
                    user=user
                )
    except Exception as e:
        frappe.log_error(
            f"Error in unbilled time reminder: {str(e)}",
            "Unbilled Time Reminder"
        )
