# -*- coding: utf-8 -*-
# Copyright (c) 2025, COMS
# License: MIT

"""
COMS Row-Level Security
=======================

Implements row-level security filters for COMS doctypes.
These filters ensure that Consultants can only see data related to 
their assigned projects, while Partners and Admins have broader access.

Used by:
- permission_query_conditions hook (for list views)
- has_permission hook (for document-level access)

Part of Phase S1: Security & Roles Implementation
"""

import frappe
from frappe import _
from frappe.utils import cint


def get_consultant_employee_id(user=None):
    """
    Get the Employee ID linked to the current (or specified) user.
    
    This is the core identifier used to filter consultant-specific data.
    Every consultant MUST have an Employee record with user_id set.
    
    Args:
        user: Username (defaults to current session user)
        
    Returns:
        str: Employee ID or None if not linked
    """
    if not user:
        user = frappe.session.user
    
    if user == "Administrator" or user == "Guest":
        return None
    
    return frappe.db.get_value("Employee", {"user_id": user}, "name")


def get_consultant_projects(user=None):
    """
    Get list of projects where current user is assigned as a consultant.
    
    Uses the Project Consultant child table populated during project setup.
    
    Args:
        user: Username (defaults to current session user)
        
    Returns:
        list: Project names the user is assigned to
    """
    employee_id = get_consultant_employee_id(user)
    if not employee_id:
        return []
    
    # Query the Project Consultant child table
    projects = frappe.db.sql("""
        SELECT DISTINCT parent as project
        FROM `tabProject Consultant`
        WHERE consultant = %s
        AND parenttype = 'Project'
    """, (employee_id,), as_dict=True)
    
    return [p.project for p in projects]


def get_consultant_client_contracts(user=None):
    """
    Get list of Client Contracts linked to consultant's projects.
    
    Args:
        user: Username (defaults to current session user)
        
    Returns:
        list: Client Contract names
    """
    projects = get_consultant_projects(user)
    if not projects:
        return []
    
    contracts = frappe.db.sql("""
        SELECT DISTINCT client_contract
        FROM `tabProject`
        WHERE name IN %(projects)s
        AND client_contract IS NOT NULL
        AND client_contract != ''
    """, {"projects": projects}, as_dict=True)
    
    return [c.client_contract for c in contracts if c.client_contract]


def _has_coms_admin_role(user=None):
    """Check if user has Consulting Admin role."""
    if not user:
        user = frappe.session.user
    return "Consulting Admin" in frappe.get_roles(user)


def _has_consulting_partner_role(user=None):
    """Check if user has Consulting Partner role."""
    if not user:
        user = frappe.session.user
    return "Consulting Partner" in frappe.get_roles(user)


def _format_in_clause(items):
    """Format a list of items for SQL IN clause."""
    if not items:
        return "''"
    return ", ".join([frappe.db.escape(item) for item in items])


# ═══════════════════════════════════════════════════════════════════════════
# PERMISSION QUERY CONDITIONS (for list views and reports)
# ═══════════════════════════════════════════════════════════════════════════

def apply_project_filter(user):
    """
    Permission query for Project doctype.
    
    Returns SQL condition to filter projects to only those 
    where the consultant is assigned.
    
    Args:
        user: Username
        
    Returns:
        str: SQL WHERE condition
    """
    # Admins and Partners see all projects
    if _has_coms_admin_role(user) or _has_consulting_partner_role(user):
        return ""
    
    projects = get_consultant_projects(user)
    if not projects:
        return "1=0"  # No access if not assigned to any project
    
    project_list = _format_in_clause(projects)
    return f"`tabProject`.name IN ({project_list})"


def apply_task_filter(user):
    """
    Permission query for Task doctype.
    
    Consultants can see tasks where:
    1. They are the assigned_consultant, OR
    2. The task belongs to one of their assigned projects
    
    Args:
        user: Username
        
    Returns:
        str: SQL WHERE condition
    """
    if _has_coms_admin_role(user) or _has_consulting_partner_role(user):
        return ""
    
    employee_id = get_consultant_employee_id(user)
    if not employee_id:
        return "1=0"
    
    projects = get_consultant_projects(user)
    project_list = _format_in_clause(projects) if projects else "''"
    
    # Escape employee_id for safe SQL
    safe_employee = frappe.db.escape(employee_id)
    
    return f"""(
        `tabTask`.assigned_consultant = {safe_employee}
        OR `tabTask`.project IN ({project_list})
    )"""


def apply_deliverable_filter(user):
    """
    Permission query for Deliverable doctype.
    
    Consultants can see deliverables where:
    1. They are the assigned_consultant, OR
    2. The deliverable belongs to one of their assigned projects
    
    Args:
        user: Username
        
    Returns:
        str: SQL WHERE condition
    """
    if _has_coms_admin_role(user) or _has_consulting_partner_role(user):
        return ""
    
    employee_id = get_consultant_employee_id(user)
    if not employee_id:
        return "1=0"
    
    projects = get_consultant_projects(user)
    project_list = _format_in_clause(projects) if projects else "''"
    safe_employee = frappe.db.escape(employee_id)
    
    return f"""(
        `tabDeliverable`.assigned_consultant = {safe_employee}
        OR `tabDeliverable`.project IN ({project_list})
    )"""


def apply_timesheet_filter(user):
    """
    Permission query for Timesheet doctype.
    
    Consultants can ONLY see their own timesheets.
    Partners can see team timesheets (controlled at higher level).
    
    Args:
        user: Username
        
    Returns:
        str: SQL WHERE condition
    """
    if _has_coms_admin_role(user):
        return ""
    
    # Partners can see timesheets for their team's projects
    if _has_consulting_partner_role(user):
        projects = get_consultant_projects(user)
        if projects:
            project_list = _format_in_clause(projects)
            return f"`tabTimesheet`.project IN ({project_list})"
        return ""
    
    # Consultants only see own timesheets
    employee_id = get_consultant_employee_id(user)
    if not employee_id:
        return "1=0"
    
    safe_employee = frappe.db.escape(employee_id)
    return f"`tabTimesheet`.employee = {safe_employee}"


def apply_client_contract_filter(user):
    """
    Permission query for Client Contract doctype.
    
    Consultants can see contracts linked to their assigned projects.
    
    Args:
        user: Username
        
    Returns:
        str: SQL WHERE condition
    """
    if _has_coms_admin_role(user) or _has_consulting_partner_role(user):
        return ""
    
    contracts = get_consultant_client_contracts(user)
    if not contracts:
        return "1=0"
    
    contract_list = _format_in_clause(contracts)
    return f"`tabClient Contract`.name IN ({contract_list})"


def apply_consultant_contract_filter(user):
    """
    Permission query for Consultant Contract doctype.
    
    Consultants can ONLY see their own contract.
    
    Args:
        user: Username
        
    Returns:
        str: SQL WHERE condition
    """
    if _has_coms_admin_role(user) or _has_consulting_partner_role(user):
        return ""
    
    employee_id = get_consultant_employee_id(user)
    if not employee_id:
        return "1=0"
    
    safe_employee = frappe.db.escape(employee_id)
    return f"`tabConsultant Contract`.consultant = {safe_employee}"


# ═══════════════════════════════════════════════════════════════════════════
# HAS PERMISSION HANDLERS (for document-level access checks)
# ═══════════════════════════════════════════════════════════════════════════

def has_project_permission(doc, user=None, permission_type=None):
    """
    Document-level permission check for Project.
    
    Args:
        doc: Project document or dict
        user: Username
        permission_type: Type of permission being checked
        
    Returns:
        bool: True if access allowed
    """
    if not user:
        user = frappe.session.user
    
    if _has_coms_admin_role(user) or _has_consulting_partner_role(user):
        return True
    
    # Check if user is assigned to this project
    project_name = doc.name if hasattr(doc, 'name') else doc.get('name')
    projects = get_consultant_projects(user)
    
    return project_name in projects


def has_deliverable_permission(doc, user=None, permission_type=None):
    """
    Document-level permission check for Deliverable.
    
    Args:
        doc: Deliverable document or dict
        user: Username
        permission_type: Type of permission being checked
        
    Returns:
        bool: True if access allowed
    """
    if not user:
        user = frappe.session.user
    
    if _has_coms_admin_role(user) or _has_consulting_partner_role(user):
        return True
    
    employee_id = get_consultant_employee_id(user)
    if not employee_id:
        return False
    
    # Get document values
    if hasattr(doc, 'assigned_consultant'):
        assigned = doc.assigned_consultant
        project = doc.project
    else:
        assigned = doc.get('assigned_consultant')
        project = doc.get('project')
    
    # Check if user is assigned consultant
    if assigned == employee_id:
        return True
    
    # Check if project is in user's assigned projects
    projects = get_consultant_projects(user)
    return project in projects


def has_timesheet_permission(doc, user=None, permission_type=None):
    """
    Document-level permission check for Timesheet.
    
    Consultants can only access their own timesheets.
    
    Args:
        doc: Timesheet document or dict
        user: Username
        permission_type: Type of permission being checked
        
    Returns:
        bool: True if access allowed
    """
    if not user:
        user = frappe.session.user
    
    if _has_coms_admin_role(user):
        return True
    
    employee_id = get_consultant_employee_id(user)
    if not employee_id:
        return False
    
    # Get employee from document
    doc_employee = doc.employee if hasattr(doc, 'employee') else doc.get('employee')
    
    # Consultants only see own
    if not _has_consulting_partner_role(user):
        return doc_employee == employee_id
    
    # Partners can see team timesheets
    projects = get_consultant_projects(user)
    doc_project = doc.project if hasattr(doc, 'project') else doc.get('project')
    
    return doc_project in projects or doc_employee == employee_id


def has_task_permission(doc, user=None, permission_type=None):
    """
    Document-level permission check for Task.
    
    Args:
        doc: Task document or dict
        user: Username
        permission_type: Type of permission being checked
        
    Returns:
        bool: True if access allowed
    """
    if not user:
        user = frappe.session.user
    
    if _has_coms_admin_role(user) or _has_consulting_partner_role(user):
        return True
    
    employee_id = get_consultant_employee_id(user)
    if not employee_id:
        return False
    
    # Get document values
    if hasattr(doc, 'assigned_consultant'):
        assigned = doc.assigned_consultant
        project = doc.project
    else:
        assigned = doc.get('assigned_consultant')
        project = doc.get('project')
    
    # Check if user is assigned consultant
    if assigned == employee_id:
        return True
    
    # Check if project is in user's assigned projects
    projects = get_consultant_projects(user)
    return project in projects
