# Copyright (c) 2025, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "project", "label": _("Project"), "fieldtype": "Link", 
         "options": "Project", "width": 200},
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link",
         "options": "Customer", "width": 150},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 80},
        {"fieldname": "contract_value", "label": _("Contract Value"), 
         "fieldtype": "Currency", "width": 120},
        {"fieldname": "revenue", "label": _("Revenue"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "time_costs", "label": _("Time Costs"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "direct_costs", "label": _("Direct Costs"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "total_costs", "label": _("Total Costs"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "gross_profit", "label": _("Gross Profit"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "margin", "label": _("Margin %"), "fieldtype": "Percent", "width": 80}
    ]


def get_data(filters):
    conditions = ""
    
    if filters.get("customer"):
        conditions += f" AND p.customer = '{filters.get('customer')}'"
    if filters.get("status"):
        conditions += f" AND p.status = '{filters.get('status')}'"
    if filters.get("from_date"):
        conditions += f" AND p.expected_start_date >= '{filters.get('from_date')}'"
    
    projects = frappe.db.sql(f"""
        SELECT p.name, p.project_name, p.customer, p.status,
               COALESCE(p.contract_value, p.estimated_costing, 0) as contract_value
        FROM `tabProject` p
        WHERE p.docstatus = 0
        {conditions}
        ORDER BY p.creation DESC
    """, as_dict=True)
    
    # Import profitability calculator
    try:
        from backend.billing.profitability import ProjectProfitabilityCalculator
        calculator = ProjectProfitabilityCalculator()
    except ImportError:
        # Fallback to simple calculation if module not available
        calculator = None
    
    data = []
    for project in projects:
        if calculator:
            try:
                metrics = calculator.calculate_project_profitability(project.name)
                data.append({
                    "project": project.name,
                    "customer": project.customer,
                    "status": project.status,
                    "contract_value": project.contract_value,
                    "revenue": metrics["revenue"],
                    "time_costs": metrics["time_costs"],
                    "direct_costs": metrics["direct_costs"],
                    "total_costs": metrics["total_costs"],
                    "gross_profit": metrics["gross_profit"],
                    "margin": metrics["gross_margin_percent"]
                })
            except Exception:
                # Skip projects that cause errors
                continue
        else:
            # Simple calculation without profitability module
            revenue = get_project_revenue(project.name)
            time_costs = get_time_costs(project.name)
            direct_costs = 0
            total_costs = time_costs + direct_costs
            gross_profit = revenue - total_costs
            margin = (gross_profit / revenue * 100) if revenue else 0
            
            data.append({
                "project": project.name,
                "customer": project.customer,
                "status": project.status,
                "contract_value": project.contract_value,
                "revenue": revenue,
                "time_costs": time_costs,
                "direct_costs": direct_costs,
                "total_costs": total_costs,
                "gross_profit": gross_profit,
                "margin": round(margin, 2)
            })
    
    return data


def get_project_revenue(project_name):
    """Get invoiced revenue for project"""
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSales Invoice`
        WHERE project = %s AND docstatus = 1
    """, (project_name,), as_dict=True)
    return flt(result[0].total) if result else 0


def get_time_costs(project_name):
    """Get time-based costs from timesheets"""
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(td.costing_amount), 0) as total
        FROM `tabTimesheet Detail` td
        INNER JOIN `tabTimesheet` ts ON ts.name = td.parent
        WHERE td.project = %s AND ts.docstatus = 1
    """, (project_name,), as_dict=True)
    return flt(result[0].total) if result else 0


def get_chart(data):
    if not data:
        return None
        
    top_projects = sorted(data, key=lambda x: flt(x.get("gross_profit", 0)), reverse=True)[:10]
    
    return {
        "data": {
            "labels": [d["project"][:20] for d in top_projects],
            "datasets": [
                {"name": _("Revenue"), "values": [d["revenue"] for d in top_projects]},
                {"name": _("Costs"), "values": [d["total_costs"] for d in top_projects]}
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#ff5858"]
    }


def get_summary(data):
    if not data:
        return []
        
    total_revenue = sum(flt(d.get("revenue", 0)) for d in data)
    total_costs = sum(flt(d.get("total_costs", 0)) for d in data)
    total_profit = total_revenue - total_costs
    avg_margin = (total_profit / total_revenue * 100) if total_revenue else 0
    
    return [
        {"label": _("Total Revenue"), "value": total_revenue, 
         "indicator": "green", "datatype": "Currency"},
        {"label": _("Total Costs"), "value": total_costs,
         "indicator": "orange", "datatype": "Currency"},
        {"label": _("Total Profit"), "value": total_profit,
         "indicator": "blue", "datatype": "Currency"},
        {"label": _("Average Margin"), "value": f"{avg_margin:.1f}%",
         "indicator": "green" if avg_margin >= 20 else "orange"}
    ]
