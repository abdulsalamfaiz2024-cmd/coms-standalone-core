# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, today


class MilestoneBillingHandler:
    """
    Handles invoice generation for contract milestones.
    
    Usage:
        handler = MilestoneBillingHandler()
        invoice = handler.generate_milestone_invoice("CONTRACT-001", "row-hash")
    """
    
    def __init__(self, company=None):
        self.company = company or frappe.defaults.get_defaults().get("company")
    
    def get_completed_milestones(self, contract_name=None):
        """
        Get milestones that are completed but not yet invoiced.
        
        Args:
            contract_name: Optional contract to filter by
        
        Returns:
            List of milestone dictionaries
        """
        milestones = []
        
        if contract_name:
            contracts = [frappe.get_doc("Client Contract", contract_name)]
        else:
            contracts = frappe.get_all(
                "Client Contract",
                filters={"status": "Active"},
                pluck="name"
            )
            contracts = [frappe.get_doc("Client Contract", c) for c in contracts]
        
        for contract in contracts:
            for milestone in contract.get("milestones", []):
                if milestone.status == "Completed" and not milestone.invoiced:
                    milestones.append({
                        "contract": contract.name,
                        "contract_title": contract.contract_title,
                        "customer": contract.client,
                        "currency": contract.currency,
                        "milestone_name": milestone.milestone_name,
                        "milestone_idx": milestone.idx,
                        "milestone_row": milestone.name,
                        "amount": milestone.amount,
                        "due_date": milestone.due_date,
                        "completed_date": milestone.completed_date,
                        "description": milestone.description
                    })
        
        return milestones
    
    def generate_milestone_invoice(self, contract_name, milestone_row_name):
        """
        Generate invoice for a specific milestone.
        
        Args:
            contract_name: Client Contract name
            milestone_row_name: Milestone child table row name
        
        Returns:
            Sales Invoice name or None
        """
        try:
            contract = frappe.get_doc("Client Contract", contract_name)
            
            # Find the milestone
            milestone = None
            for m in contract.get("milestones", []):
                if m.name == milestone_row_name:
                    milestone = m
                    break
            
            if not milestone:
                frappe.throw(_("Milestone not found"))
            
            if milestone.invoiced:
                frappe.throw(_("Milestone already invoiced"))
            
            if milestone.status != "Completed":
                frappe.throw(_("Milestone must be completed before invoicing"))
            
            # Create invoice
            invoice = frappe.new_doc("Sales Invoice")
            invoice.customer = contract.client
            invoice.company = self.company
            invoice.posting_date = today()
            invoice.currency = contract.currency
            invoice.is_consulting = 1
            invoice.billing_type = "Milestone"
            invoice.client_contract = contract_name
            
            # Get linked project if exists
            if contract.get("projects") and len(contract.projects) > 0:
                invoice.project = contract.projects[0].project
            
            # Payment terms from contract
            if hasattr(contract, 'payment_terms_template') and contract.payment_terms_template:
                invoice.payment_terms_template = contract.payment_terms_template
            
            # Get or create milestone billing item
            item_code = self.get_milestone_item()
            
            # Build description
            description = self.build_milestone_description(contract, milestone)
            
            # Add line item
            invoice.append("items", {
                "item_code": item_code,
                "description": description,
                "qty": 1,
                "rate": milestone.amount,
                "amount": milestone.amount
            })
            
            invoice.flags.ignore_permissions = True
            invoice.insert()
            
            # Mark milestone as invoiced
            milestone.invoiced = 1
            milestone.status = "Invoiced"
            contract.save(ignore_permissions=True)
            
            # Update contract invoiced amount
            self.update_contract_amounts(contract)
            
            return invoice.name
            
        except Exception as e:
            frappe.log_error(
                f"Milestone invoice error: {str(e)}",
                "Milestone Billing"
            )
            raise
    
    def get_milestone_item(self):
        """Get or create milestone billing item"""
        item_code = "Milestone Payment"
        
        if not frappe.db.exists("Item", item_code):
            item = frappe.new_doc("Item")
            item.item_code = item_code
            item.item_name = "Milestone Payment"
            item.item_group = "Services"
            item.stock_uom = "Nos"
            item.is_stock_item = 0
            item.is_sales_item = 1
            item.insert(ignore_permissions=True)
        
        return item_code
    
    def build_milestone_description(self, contract, milestone):
        """Build invoice line description"""
        parts = [
            f"Contract: {contract.contract_title}",
            f"Milestone: {milestone.milestone_name}",
        ]
        
        if milestone.description:
            parts.append(f"Description: {milestone.description}")
        
        if milestone.completed_date:
            parts.append(f"Completed: {frappe.format_date(milestone.completed_date)}")
        
        return "\n".join(parts)
    
    def update_contract_amounts(self, contract):
        """Update contract invoiced/paid amounts"""
        # This is handled by the invoice_events.py
        try:
            from backend.events.invoice_events import update_contract_amounts
            update_contract_amounts(contract.name)
        except Exception:
            pass  # If function not available yet, skip
    
    def generate_all_pending_milestone_invoices(self):
        """Generate invoices for all completed milestones"""
        milestones = self.get_completed_milestones()
        invoices = []
        errors = []
        
        for ms in milestones:
            try:
                invoice = self.generate_milestone_invoice(
                    ms["contract"],
                    ms["milestone_row"]
                )
                if invoice:
                    invoices.append(invoice)
            except Exception as e:
                errors.append(f"{ms['contract']}/{ms['milestone_name']}: {str(e)}")
        
        return {
            "invoices": invoices,
            "errors": errors
        }


# Whitelisted API methods

@frappe.whitelist()
def get_pending_milestones(contract=None):
    """Get milestones ready for invoicing"""
    handler = MilestoneBillingHandler()
    return handler.get_completed_milestones(contract)


@frappe.whitelist()
def generate_milestone_invoice(contract, milestone_row):
    """Generate invoice for a milestone"""
    handler = MilestoneBillingHandler()
    invoice = handler.generate_milestone_invoice(contract, milestone_row)
    
    if invoice:
        frappe.msgprint(
            _("Invoice {0} created").format(invoice),
            indicator="green"
        )
    
    return invoice


@frappe.whitelist()
def complete_milestone(contract, milestone_row):
    """
    Mark a milestone as completed.
    Called from Contract or Project UI.
    """
    contract_doc = frappe.get_doc("Client Contract", contract)
    
    for milestone in contract_doc.get("milestones", []):
        if milestone.name == milestone_row:
            if milestone.status == "Completed":
                frappe.throw(_("Milestone already completed"))
            
            milestone.status = "Completed"
            milestone.completed_date = today()
            break
    
    contract_doc.save()
    
    frappe.msgprint(_("Milestone marked as completed"))
    
    return True
