# -*- coding: utf-8 -*-
# Copyright (c) 2025, COMS
# License: MIT

"""
S1 Phase Script: Apply COMS Permissions
=======================================

This script applies the COMS permission matrix to all relevant doctypes.
It adds the permission rules for Consultant, Consulting Partner, and 
Consulting Admin roles.

Execution:
    bench execute coms_setup_files.phase_scripts.s1_apply_permissions.execute
    
Or from bench console:
    from coms_setup_files.phase_scripts.s1_apply_permissions import apply_all_permissions
    apply_all_permissions()

Part of Phase S1: Security & Roles Implementation
"""

import frappe
from frappe import _
import json

# Import the permission matrix
try:
    from backend.security.permissions import PERMISSION_MATRIX, get_permissions_for_role
except ImportError:
    # Fallback if not installed yet
    PERMISSION_MATRIX = {}
    def get_permissions_for_role(dt, role):
        return PERMISSION_MATRIX.get(dt, {}).get(role, {})


# Doctypes that need permission updates applied directly to their JSON
COMS_CUSTOM_DOCTYPES = [
    "Client Contract",
    "Consultant Contract",
    "Deliverable",
    "Expertise Area"
]

# Standard ERPNext doctypes that need Custom DocPerm records
STANDARD_DOCTYPES = [
    "Project",
    "Task", 
    "Timesheet",
    "Sales Invoice",
    "Employee",
    "Customer"
]

# All COMS roles
COMS_ROLES = ["Consultant", "Consulting Partner", "Consulting Admin"]


def apply_custom_docperm(doctype, role, permissions):
    """
    Apply or update Custom DocPerm for a standard ERPNext doctype.
    
    Args:
        doctype: DocType name
        role: Role name
        permissions: Permission dict
        
    Returns:
        bool: Success status
    """
    if not permissions:
        return False
    
    # Check if Custom DocPerm already exists
    existing = frappe.db.get_value(
        "Custom DocPerm",
        {"parent": doctype, "role": role, "permlevel": 0},
        "name"
    )
    
    if existing:
        # Update existing
        doc = frappe.get_doc("Custom DocPerm", existing)
        for key, value in permissions.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        doc.save(ignore_permissions=True)
        print(f"    → Updated Custom DocPerm for {role}")
    else:
        # Create new Custom DocPerm
        doc = frappe.new_doc("Custom DocPerm")
        doc.parent = doctype
        doc.parenttype = "DocType"
        doc.parentfield = "permissions"
        doc.role = role
        doc.permlevel = 0
        
        for key, value in permissions.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        
        doc.insert(ignore_permissions=True)
        print(f"    → Created Custom DocPerm for {role}")
    
    return True


def apply_doctype_permissions(doctype, permissions_dict):
    """
    Apply permissions to a custom doctype by updating its JSON definition.
    
    For COMS custom doctypes, we update the permissions array directly.
    
    Args:
        doctype: DocType name
        permissions_dict: Dict of role -> permissions
        
    Returns:
        bool: Success status
    """
    if not frappe.db.exists("DocType", doctype):
        print(f"    ✗ DocType {doctype} not found")
        return False
    
    # Get the doctype document
    dt = frappe.get_doc("DocType", doctype)
    
    for role, perms in permissions_dict.items():
        if not perms:
            continue
        
        # Check if permission already exists for this role
        existing_perm = None
        for p in dt.permissions:
            if p.role == role:
                existing_perm = p
                break
        
        if existing_perm:
            # Update existing permission
            for key, value in perms.items():
                if hasattr(existing_perm, key):
                    setattr(existing_perm, key, value)
            print(f"    → Updated permission for {role}")
        else:
            # Add new permission
            perm_row = {
                "role": role,
                "permlevel": 0
            }
            perm_row.update(perms)
            dt.append("permissions", perm_row)
            print(f"    → Added permission for {role}")
    
    dt.save(ignore_permissions=True)
    return True


def apply_all_permissions():
    """
    Apply all COMS permissions as defined in the permission matrix.
    
    Returns:
        dict: Summary of applied permissions
    """
    print("\n" + "=" * 60)
    print("COMS Phase S1: Applying Permissions")
    print("=" * 60 + "\n")
    
    results = {
        "custom_doctypes": [],
        "standard_doctypes": [],
        "errors": []
    }
    
    # First verify roles exist
    for role in COMS_ROLES:
        if not frappe.db.exists("Role", role):
            error = f"Role {role} does not exist. Run s1_create_roles.py first."
            print(f"  ✗ {error}")
            results["errors"].append(error)
            return results
    
    print("Applying permissions to COMS Custom Doctypes:")
    print("-" * 40)
    
    # Apply to COMS custom doctypes
    for doctype in COMS_CUSTOM_DOCTYPES:
        print(f"\n  {doctype}:")
        try:
            permissions = PERMISSION_MATRIX.get(doctype, {})
            if permissions:
                apply_doctype_permissions(doctype, permissions)
                results["custom_doctypes"].append(doctype)
            else:
                print(f"    ○ No permissions defined")
        except Exception as e:
            error = f"Error applying permissions to {doctype}: {str(e)}"
            print(f"    ✗ {error}")
            results["errors"].append(error)
    
    print("\n\nApplying Custom DocPerms to Standard ERPNext Doctypes:")
    print("-" * 40)
    
    # Apply Custom DocPerm to standard doctypes
    for doctype in STANDARD_DOCTYPES:
        print(f"\n  {doctype}:")
        try:
            perm_dict = PERMISSION_MATRIX.get(doctype, {})
            
            for role in COMS_ROLES:
                perms = perm_dict.get(role, {})
                if perms:
                    apply_custom_docperm(doctype, role, perms)
            
            if doctype not in results["standard_doctypes"]:
                results["standard_doctypes"].append(doctype)
                
        except Exception as e:
            error = f"Error with {doctype}: {str(e)}"
            print(f"    ✗ {error}")
            results["errors"].append(error)
    
    frappe.db.commit()
    
    print("\n" + "=" * 60)
    print("Permissions Applied Summary:")
    print(f"  - Custom Doctypes: {len(results['custom_doctypes'])}")
    print(f"  - Standard Doctypes: {len(results['standard_doctypes'])}")
    print(f"  - Errors: {len(results['errors'])}")
    print("=" * 60 + "\n")
    
    return results


def clear_coms_permissions():
    """
    Remove all COMS role permissions.
    Use with caution - for development/testing only.
    
    Returns:
        dict: Summary
    """
    print("\n" + "=" * 60)
    print("COMS Phase S1: Clearing Permissions (DEVELOPMENT ONLY)")
    print("=" * 60 + "\n")
    
    removed = []
    
    for role in COMS_ROLES:
        # Remove Custom DocPerm entries
        count = frappe.db.count("Custom DocPerm", {"role": role})
        if count:
            frappe.db.delete("Custom DocPerm", {"role": role})
            removed.append(f"Removed {count} Custom DocPerm entries for {role}")
            print(f"  ✓ Removed {count} Custom DocPerm for {role}")
    
    frappe.db.commit()
    
    print(f"\nTotal actions: {len(removed)}")
    return {"removed": removed}


def verify_permissions():
    """
    Verify that permissions are correctly applied.
    
    Returns:
        dict: Verification results
    """
    print("\n" + "=" * 60)
    print("COMS Phase S1: Verifying Permissions")
    print("=" * 60 + "\n")
    
    results = []
    all_valid = True
    
    all_doctypes = COMS_CUSTOM_DOCTYPES + STANDARD_DOCTYPES
    
    for doctype in all_doctypes:
        print(f"\n{doctype}:")
        doctype_valid = True
        
        expected_perms = PERMISSION_MATRIX.get(doctype, {})
        
        for role, expected in expected_perms.items():
            if not expected:
                continue
            
            # Check if permission exists
            if doctype in COMS_CUSTOM_DOCTYPES:
                # Check DocType permissions
                dt = frappe.get_doc("DocType", doctype)
                found = any(p.role == role for p in dt.permissions)
            else:
                # Check Custom DocPerm
                found = frappe.db.exists("Custom DocPerm", {
                    "parent": doctype,
                    "role": role
                })
            
            if found:
                print(f"  ✓ {role}")
            else:
                print(f"  ✗ {role} - NOT FOUND")
                doctype_valid = False
                all_valid = False
        
        results.append({
            "doctype": doctype,
            "valid": doctype_valid
        })
    
    print("\n" + "=" * 60)
    print(f"Overall: {'✓ All permissions applied' if all_valid else '✗ Some permissions missing'}")
    print("=" * 60 + "\n")
    
    return {
        "results": results,
        "all_valid": all_valid
    }


def execute():
    """
    Main execution function for bench execute command.
    """
    return apply_all_permissions()


if __name__ == "__main__":
    execute()
