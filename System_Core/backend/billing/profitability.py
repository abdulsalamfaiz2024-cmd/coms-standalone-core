# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


class ProjectProfitabilityCalculator:
    """
    Calculate project profitability metrics.
    
    Profitability = Revenue - Costs
    
    Revenue sources:
    - Invoiced amounts from Sales Invoice
    
    Cost sources:
    - Timesheet costing amounts
    - Direct project costs (Purchase Invoice, Expense Claims)
    """
    
    def calculate_project_profitability(self, project_name):
        """
        Calculate profitability for a project.
        
        Returns:
            dict with profitability metrics
        """
        project = frappe.get_doc("Project", project_name)
        
        # Revenue from invoices
        revenue = self.get_project_revenue(project_name)
        
        # Time costs
        time_costs = self.get_time_costs(project_name)
        
        # Direct costs
        direct_costs = self.get_direct_costs(project_name)
        
        # Calculate totals
        total_costs = time_costs + direct_costs
        gross_profit = revenue - total_costs
        gross_margin = (gross_profit / revenue * 100) if revenue else 0
        
        return {
            "project": project_name,
            "revenue": revenue,
            "time_costs": time_costs,
            "direct_costs": direct_costs,
            "total_costs": total_costs,
            "gross_profit": gross_profit,
            "gross_margin_percent": round(gross_margin, 2),
            "contract_value": flt(getattr(project, 'contract_value', 0)) or flt(project.estimated_costing),
            "budget_variance": (flt(getattr(project, 'contract_value', 0)) or flt(project.estimated_costing)) - total_costs
        }
    
    def get_project_revenue(self, project_name):
        """Get invoiced revenue for project"""
        result = frappe.db.sql("""
            SELECT COALESCE(SUM(grand_total), 0) as total
            FROM `tabSales Invoice`
            WHERE project = %s
            AND docstatus = 1
        """, (project_name,), as_dict=True)
        
        return flt(result[0].total) if result else 0
    
    def get_time_costs(self, project_name):
        """Get time-based costs from timesheets"""
        result = frappe.db.sql("""
            SELECT COALESCE(SUM(td.costing_amount), 0) as total
            FROM `tabTimesheet Detail` td
            INNER JOIN `tabTimesheet` ts ON ts.name = td.parent
            WHERE td.project = %s
            AND ts.docstatus = 1
        """, (project_name,), as_dict=True)
        
        return flt(result[0].total) if result else 0
    
    def get_direct_costs(self, project_name):
        """
        Get direct costs from:
        - Purchase Invoices
        - Expense Claims
        - Project expenses (if using project costing)
        """
        total = 0
        
        # Purchase Invoice costs
        pi_costs = frappe.db.sql("""
            SELECT COALESCE(SUM(grand_total), 0) as total
            FROM `tabPurchase Invoice`
            WHERE project = %s
            AND docstatus = 1
        """, (project_name,), as_dict=True)
        
        total += flt(pi_costs[0].total) if pi_costs else 0
        
        # Expense claims
        expense_costs = frappe.db.sql("""
            SELECT COALESCE(SUM(total_claimed_amount), 0) as total
            FROM `tabExpense Claim`
            WHERE project = %s
            AND docstatus = 1
        """, (project_name,), as_dict=True)
        
        total += flt(expense_costs[0].total) if expense_costs else 0
        
        return total
    
    def update_project_profitability_fields(self, project_name):
        """Update profitability custom fields on project"""
        metrics = self.calculate_project_profitability(project_name)
        
        # Update project (assumes custom fields exist)
        frappe.db.set_value(
            "Project",
            project_name,
            {
                "actual_gross_margin": metrics["gross_margin_percent"]
            },
            update_modified=False
        )
        
        return metrics
    
    def get_contract_profitability(self, contract_name):
        """Calculate profitability for all projects in a contract"""
        contract = frappe.get_doc("Client Contract", contract_name)
        
        total_revenue = 0
        total_costs = 0
        project_metrics = []
        
        for project_row in contract.get("projects", []):
            metrics = self.calculate_project_profitability(project_row.project)
            project_metrics.append(metrics)
            total_revenue += metrics["revenue"]
            total_costs += metrics["total_costs"]
        
        gross_profit = total_revenue - total_costs
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue else 0
        
        return {
            "contract": contract_name,
            "contract_value": contract.contract_value,
            "total_revenue": total_revenue,
            "total_costs": total_costs,
            "gross_profit": gross_profit,
            "gross_margin_percent": round(gross_margin, 2),
            "projects": project_metrics
        }


# Whitelisted API methods

@frappe.whitelist()
def get_project_profitability(project):
    """Get profitability metrics for a project"""
    calculator = ProjectProfitabilityCalculator()
    return calculator.calculate_project_profitability(project)


@frappe.whitelist()
def get_contract_profitability(contract):
    """Get profitability metrics for a contract"""
    calculator = ProjectProfitabilityCalculator()
    return calculator.get_contract_profitability(contract)


@frappe.whitelist()
def refresh_project_profitability(project):
    """Recalculate and update project profitability"""
    calculator = ProjectProfitabilityCalculator()
    return calculator.update_project_profitability_fields(project)
