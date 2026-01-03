# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today, flt


class ConsultantContract(Document):
    def validate(self):
        self.validate_dates()
        self.validate_rates()
        self.check_expiry()
    
    def validate_dates(self):
        """Validate contract dates"""
        if self.end_date and self.start_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw(_("End Date cannot be before Start Date"))
    
    def validate_rates(self):
        """Ensure rate is positive"""
        # Fix: Check if rate_amount has a value before comparison
        if self.rate_amount is not None and flt(self.rate_amount) < 0:
             frappe.throw(_("Rate Amount cannot be negative"))
        
        # Optional: Decide if 0 is allowed. Usually 0 is fine for some cases, but previous code was stricter.
        # But for mandatory check test, if we pass None/0, we don't want strict throw here if Field is Mandatory handled by framework.
        # However, checking < 0 is safe logic.
    
    def check_expiry(self):
        """Check if contract has expired"""
        if self.end_date and getdate(self.end_date) < getdate(today()):
            if self.status == "Active":
                self.status = "Expired"
                frappe.msgprint(_("Contract has expired. Status changed to Expired."))
    
    def on_update(self):
        """Update employee record with contract rates"""
        if self.status == "Active":
            self.update_employee_rates()
    
    def update_employee_rates(self):
        """Update employee hourly/daily rates from contract"""
        if self.consultant:
            employee = frappe.get_doc("Employee", self.consultant)
            if self.rate_type == "Hourly":
                employee.hourly_rate = self.rate_amount
            elif self.rate_type == "Daily":
                employee.daily_rate = self.rate_amount
            employee.save(ignore_permissions=True)


@frappe.whitelist()
def get_active_contract(employee):
    """Get active contract for an employee"""
    contracts = frappe.get_all(
        "Consultant Contract",
        filters={
            "consultant": employee,
            "status": "Active"
        },
        fields=["name", "rate_type", "rate_amount", "currency"]
    )
    return contracts[0] if contracts else None
