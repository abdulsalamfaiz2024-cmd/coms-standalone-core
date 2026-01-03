# -*- coding: utf-8 -*-
# Copyright (c) 2025, COMS
# License: MIT

"""
COMS Role Definitions
=====================

Defines the three principal roles for the Consultant Portal separation:
1. Consultant - Portal user with limited access to own data
2. Consulting Partner - Senior consultant with managerial access
3. Consulting Admin - Full administrative access to COMS module

Part of Phase S1: Security & Roles Implementation
"""

import frappe
from frappe import _

# Role configuration definitions
COMS_ROLES = [
    {
        "role_name": "Consultant",
        "desk_access": 0,  # Portal only - no Desk access
        "is_custom": 1,
        "disabled": 0,
        "description": "External or internal consultant with limited portal access. Can view and manage own tasks, timesheets, and deliverables only."
    },
    {
        "role_name": "Consulting Partner",
        "desk_access": 1,  # Desk access for management functions
        "is_custom": 1,
        "disabled": 0,
        "description": "Senior consultant or partner with managerial access. Can view all project data, approve deliverables, and manage team members."
    },
    {
        "role_name": "Consulting Admin",
        "desk_access": 1,  # Full desk access
        "is_custom": 1,
        "disabled": 0,
        "description": "Full COMS administrative access. Can manage all consulting operations, assign consultants, configure settings."
    }
]

# Role hierarchy for permission escalation
ROLE_HIERARCHY = {
    "Consultant": 1,           # Base level
    "Consulting Partner": 2,   # Mid level - includes Consultant permissions
    "Consulting Admin": 3      # Top level - includes all permissions
}


def get_role_config(role_name):
    """
    Get configuration for a specific COMS role.
    
    Args:
        role_name: Name of the role to retrieve
        
    Returns:
        dict: Role configuration or None if not found
    """
    for role in COMS_ROLES:
        if role["role_name"] == role_name:
            return role.copy()
    return None


def get_role_level(role_name):
    """
    Get the hierarchy level of a role.
    Higher number = more permissions.
    
    Args:
        role_name: Name of the role
        
    Returns:
        int: Role level (0 if not a COMS role)
    """
    return ROLE_HIERARCHY.get(role_name, 0)


def get_user_highest_coms_role(user=None):
    """
    Get the highest-level COMS role for a user.
    
    Args:
        user: Username (defaults to current session user)
        
    Returns:
        str: Highest COMS role name or None
    """
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    highest_role = None
    highest_level = 0
    
    for role_name, level in ROLE_HIERARCHY.items():
        if role_name in user_roles and level > highest_level:
            highest_role = role_name
            highest_level = level
    
    return highest_role


def is_consultant(user=None):
    """Check if user has Consultant role."""
    if not user:
        user = frappe.session.user
    return "Consultant" in frappe.get_roles(user)


def is_consulting_partner(user=None):
    """Check if user has Consulting Partner role."""
    if not user:
        user = frappe.session.user
    return "Consulting Partner" in frappe.get_roles(user)


def is_consulting_admin(user=None):
    """Check if user has Consulting Admin role."""
    if not user:
        user = frappe.session.user
    return "Consulting Admin" in frappe.get_roles(user)


def has_any_coms_role(user=None):
    """Check if user has any COMS role."""
    if not user:
        user = frappe.session.user
    user_roles = set(frappe.get_roles(user))
    coms_roles = set(ROLE_HIERARCHY.keys())
    return bool(user_roles & coms_roles)


def validate_role_assignment(user, role_name):
    """
    Validate if a role can be assigned to a user.
    
    Args:
        user: Username
        role_name: Role to assign
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if role_name not in ROLE_HIERARCHY:
        return False, _("Invalid COMS role: {0}").format(role_name)
    
    # Check if user has Employee linked
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee and role_name in ["Consultant", "Consulting Partner"]:
        return False, _("User must have an Employee record linked to be assigned {0} role").format(role_name)
    
    return True, None
