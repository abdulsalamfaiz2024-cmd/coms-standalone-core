# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today, getdate


class ConsultingInvoiceGenerator:
    """
    Generates Sales Invoices from submitted Timesheets.
    
    Usage:
        generator = ConsultingInvoiceGenerator()
        invoices = generator.generate_invoices_for_project("PROJECT-001")
        
    Or for batch processing:
        generator = ConsultingInvoiceGenerator()
        invoices = generator.generate_all_pending_invoices()
    """
    
    def __init__(self, company=None):
        self.company = company or frappe.defaults.get_defaults().get("company")
        self.errors = []
        self.generated_invoices = []
    
    def get_unbilled_timesheet_entries(self, filters=None):
        """
        Get all unbilled timesheet entries.
        
        Args:
            filters: dict with optional keys: project, customer, from_date, to_date
        
        Returns:
            List of unbilled timesheet detail entries
        """
        conditions = """
            td.billable = 1
            AND td.sales_invoice IS NULL
            AND ts.docstatus = 1
        """
        
        if filters:
            if filters.get("project"):
                conditions += f" AND td.project = '{filters['project']}'"
            if filters.get("customer"):
                conditions += f" AND ts.customer = '{filters['customer']}'"
            if filters.get("from_date"):
                conditions += f" AND td.from_time >= '{filters['from_date']}'"
            if filters.get("to_date"):
                conditions += f" AND td.to_time <= '{filters['to_date']}'"
        
        entries = frappe.db.sql(f"""
            SELECT 
                td.name as detail_name,
                td.parent as timesheet,
                td.project,
                td.task,
                td.activity_type,
                td.hours,
                td.billing_hours,
                td.billing_rate,
                td.billing_amount,
                td.from_time,
                td.to_time,
                td.description,
                ts.employee,
                ts.employee_name,
                ts.customer,
                ts.consultant_contract,
                p.client_contract,
                p.customer as project_customer
            FROM `tabTimesheet Detail` td
            INNER JOIN `tabTimesheet` ts ON ts.name = td.parent
            LEFT JOIN `tabProject` p ON p.name = td.project
            WHERE {conditions}
            ORDER BY ts.customer, td.project, td.from_time
        """, as_dict=True)
        
        return entries
    
    def group_entries_by_customer_project(self, entries):
        """
        Group timesheet entries by customer and project.
        
        Returns:
            dict: {customer: {project: [entries]}}
        """
        grouped = {}
        
        for entry in entries:
            # Determine customer
            customer = entry.customer or entry.project_customer
            
            if not customer:
                self.errors.append(
                    f"Entry {entry.detail_name}: No customer found"
                )
                continue
            
            if customer not in grouped:
                grouped[customer] = {}
            
            project = entry.project or "No Project"
            
            if project not in grouped[customer]:
                grouped[customer][project] = []
            
            grouped[customer][project].append(entry)
        
        return grouped
    
    def create_invoice(self, customer, project, entries):
        """
        Create a Sales Invoice for the given entries.
        
        Args:
            customer: Customer name
            project: Project name
            entries: List of timesheet entries
        
        Returns:
            Sales Invoice name or None on error
        """
        try:
            # Get customer and project details
            customer_doc = frappe.get_doc("Customer", customer)
            project_doc = frappe.get_doc("Project", project) if project != "No Project" else None
            
            # Create invoice
            invoice = frappe.new_doc("Sales Invoice")
            invoice.customer = customer
            invoice.company = self.company
            invoice.posting_date = today()
            invoice.due_date = today()  # Will be updated by payment terms
            invoice.is_consulting = 1
            invoice.billing_type = "Time-Based"
            
            if project_doc:
                invoice.project = project
                if hasattr(project_doc, 'client_contract') and project_doc.client_contract:
                    invoice.client_contract = project_doc.client_contract
                    # Get payment terms from contract
                    if frappe.db.exists("Client Contract", project_doc.client_contract):
                        contract = frappe.get_doc("Client Contract", project_doc.client_contract)
                        if hasattr(contract, 'payment_terms_template') and contract.payment_terms_template:
                            invoice.payment_terms_template = contract.payment_terms_template
            
            # Determine the billing item
            billing_item = self.get_billing_item()
            
            # Add line items for each entry
            for entry in entries:
                hours = flt(entry.billing_hours or entry.hours)
                rate = flt(entry.billing_rate)
                amount = flt(entry.billing_amount) or (hours * rate)
                
                # Build description
                description = self.build_item_description(entry)
                
                invoice.append("items", {
                    "item_code": billing_item,
                    "description": description,
                    "qty": hours,
                    "rate": rate,
                    "amount": amount,
                    "timesheet": entry.timesheet,
                    "ts_detail": entry.detail_name,
                    "consultant": entry.employee,
                    "hours_billed": hours
                })
            
            invoice.flags.ignore_permissions = True
            invoice.insert()
            
            # Update timesheet entries with invoice reference
            self.link_entries_to_invoice(entries, invoice.name)
            
            self.generated_invoices.append(invoice.name)
            
            return invoice.name
            
        except Exception as e:
            self.errors.append(
                f"Error creating invoice for {customer}/{project}: {str(e)}"
            )
            frappe.log_error(
                f"Invoice generation error: {str(e)}",
                "Consulting Invoice Generator"
            )
            return None
    
    def get_billing_item(self):
        """Get or create the consulting service item"""
        item_code = "Consulting Services"
        
        if not frappe.db.exists("Item", item_code):
            item = frappe.new_doc("Item")
            item.item_code = item_code
            item.item_name = "Consulting Services"
            item.item_group = "Services"
            item.stock_uom = "Hour"
            item.is_stock_item = 0
            item.is_sales_item = 1
            item.include_item_in_manufacturing = 0
            item.insert(ignore_permissions=True)
        
        return item_code
    
    def build_item_description(self, entry):
        """Build line item description from entry"""
        parts = []
        
        if entry.employee_name:
            parts.append(f"Consultant: {entry.employee_name}")
        
        if entry.project:
            parts.append(f"Project: {entry.project}")
        
        if entry.task:
            parts.append(f"Task: {entry.task}")
        
        if entry.activity_type:
            parts.append(f"Activity: {entry.activity_type}")
        
        date_str = frappe.format_date(getdate(entry.from_time))
        parts.append(f"Date: {date_str}")
        
        if entry.description:
            parts.append(f"Notes: {entry.description[:100]}")
        
        return "\n".join(parts)
    
    def link_entries_to_invoice(self, entries, invoice_name):
        """Update timesheet entries with invoice reference"""
        for entry in entries:
            frappe.db.set_value(
                "Timesheet Detail",
                entry.detail_name,
                "sales_invoice",
                invoice_name,
                update_modified=False
            )
    
    def generate_invoices_for_project(self, project):
        """Generate invoice for a specific project"""
        entries = self.get_unbilled_timesheet_entries({"project": project})
        
        if not entries:
            return []
        
        grouped = self.group_entries_by_customer_project(entries)
        
        for customer, projects in grouped.items():
            for proj, proj_entries in projects.items():
                self.create_invoice(customer, proj, proj_entries)
        
        return self.generated_invoices
    
    def generate_invoices_for_customer(self, customer):
        """Generate invoices for a specific customer"""
        entries = self.get_unbilled_timesheet_entries({"customer": customer})
        
        if not entries:
            return []
        
        grouped = self.group_entries_by_customer_project(entries)
        
        if customer in grouped:
            for project, proj_entries in grouped[customer].items():
                self.create_invoice(customer, project, proj_entries)
        
        return self.generated_invoices
    
    def generate_all_pending_invoices(self):
        """Generate invoices for all unbilled time entries"""
        entries = self.get_unbilled_timesheet_entries()
        
        if not entries:
            frappe.msgprint(_("No unbilled time entries found"))
            return []
        
        grouped = self.group_entries_by_customer_project(entries)
        
        for customer, projects in grouped.items():
            for project, proj_entries in projects.items():
                self.create_invoice(customer, project, proj_entries)
        
        if self.errors:
            frappe.msgprint(
                _("Completed with errors:\n") + "\n".join(self.errors),
                indicator="orange"
            )
        
        return self.generated_invoices


# Whitelisted functions for API/UI access

@frappe.whitelist()
def generate_invoice_for_project(project):
    """API method to generate invoice for a project"""
    generator = ConsultingInvoiceGenerator()
    invoices = generator.generate_invoices_for_project(project)
    
    if invoices:
        frappe.msgprint(
            _("Created {0} invoice(s): {1}").format(
                len(invoices),
                ", ".join(invoices)
            ),
            indicator="green"
        )
    else:
        frappe.msgprint(_("No unbilled entries found"))
    
    return invoices


@frappe.whitelist()
def generate_invoice_for_customer(customer):
    """API method to generate invoices for a customer"""
    generator = ConsultingInvoiceGenerator()
    invoices = generator.generate_invoices_for_customer(customer)
    
    if invoices:
        frappe.msgprint(
            _("Created {0} invoice(s)").format(len(invoices)),
            indicator="green"
        )
    
    return invoices


@frappe.whitelist()
def generate_all_invoices():
    """API method to generate all pending invoices"""
    generator = ConsultingInvoiceGenerator()
    invoices = generator.generate_all_pending_invoices()
    
    return {
        "invoices": invoices,
        "errors": generator.errors
    }


@frappe.whitelist()
def get_unbilled_summary():
    """Get summary of unbilled time entries"""
    generator = ConsultingInvoiceGenerator()
    entries = generator.get_unbilled_timesheet_entries()
    
    summary = {
        "total_entries": len(entries),
        "total_hours": sum(flt(e.billing_hours or e.hours) for e in entries),
        "total_amount": sum(flt(e.billing_amount) for e in entries),
        "by_customer": {},
        "by_project": {}
    }
    
    for entry in entries:
        customer = entry.customer or entry.project_customer or "Unknown"
        project = entry.project or "No Project"
        
        if customer not in summary["by_customer"]:
            summary["by_customer"][customer] = {"hours": 0, "amount": 0}
        
        summary["by_customer"][customer]["hours"] += flt(entry.billing_hours or entry.hours)
        summary["by_customer"][customer]["amount"] += flt(entry.billing_amount)
        
        if project not in summary["by_project"]:
            summary["by_project"][project] = {"hours": 0, "amount": 0}
        
        summary["by_project"][project]["hours"] += flt(entry.billing_hours or entry.hours)
        summary["by_project"][project]["amount"] += flt(entry.billing_amount)
    
    return summary
