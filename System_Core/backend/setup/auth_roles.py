# -*- coding: utf-8 -*-
# Copyright (c) 2025, COMS
# License: MIT

"""
S1 Phase Script: Create COMS Roles
==================================

This script creates the three principal roles for the COMS Consultant Portal:
1. Consultant - Portal user with limited access
2. Consulting Partner - Senior consultant with managerial access
3. Consulting Admin - Full administrative access

Execution:
    bench execute coms_setup_files.phase_scripts.s1_create_roles.execute
    
Or from bench console:
    from coms_setup_files.phase_scripts.s1_create_roles import create_roles
    create_roles()

Part of Phase S1: Security & Roles Implementation
"""

import frappe
from frappe import _

# Role definitions with full configuration
COMS_ROLES = [
    {
        "role_name": "Consultant",
        "desk_access": 0,  # Portal only - no Desk access
        "is_custom": 1,
        "disabled": 0,
        "two_factor_auth": 0,
        "description": "External or internal consultant with limited portal access. Can view and manage own tasks, timesheets, and deliverables only. No access to ERPNext Desk."
    },
    {
        "role_name": "Consulting Partner",
        "desk_access": 1,  # Desk access for management functions
        "is_custom": 1,
        "disabled": 0,
        "two_factor_auth": 0,
        "description": "Senior consultant or partner with managerial access. Can view all project data, approve deliverables, and manage team members. Has ERPNext Desk access."
    },
    {
        "role_name": "Consulting Admin",
        "desk_access": 1,  # Full desk access
        "is_custom": 1,
        "disabled": 0,
        "two_factor_auth": 0,
        "description": "Full COMS administrative access. Can manage all consulting operations, assign consultants, configure settings, and has complete ERPNext Desk access."
    }
]


def create_roles():
    """
    Create all COMS roles in the database.
    
    Returns:
        dict: Summary of created/existing roles
    """
    created = []
    existing = []
    errors = []
    
    print("\n" + "=" * 60)
    print("COMS Phase S1: Creating Roles")
    print("=" * 60 + "\n")
    
    for role_data in COMS_ROLES:
        role_name = role_data["role_name"]
        
        try:
            if frappe.db.exists("Role", role_name):
                # Update existing role if needed
                role = frappe.get_doc("Role", role_name)
                updated = False
                
                for key, value in role_data.items():
                    if key != "role_name" and getattr(role, key, None) != value:
                        setattr(role, key, value)
                        updated = True
                
                if updated:
                    role.save(ignore_permissions=True)
                    print(f"  ✓ Updated role: {role_name}")
                else:
                    print(f"  ○ Role exists (unchanged): {role_name}")
                
                existing.append(role_name)
            else:
                # Create new role
                role = frappe.new_doc("Role")
                role.role_name = role_data["role_name"]
                role.desk_access = role_data.get("desk_access", 0)
                role.is_custom = role_data.get("is_custom", 1)
                role.disabled = role_data.get("disabled", 0)
                role.two_factor_auth = role_data.get("two_factor_auth", 0)
                
                role.insert(ignore_permissions=True)
                print(f"  ✓ Created role: {role_name}")
                created.append(role_name)
                
        except Exception as e:
            error_msg = f"Error with role {role_name}: {str(e)}"
            print(f"  ✗ {error_msg}")
            errors.append(error_msg)
    
    frappe.db.commit()
    
    summary = {
        "created": created,
        "existing": existing,
        "errors": errors,
        "success": len(errors) == 0
    }
    
    print("\n" + "-" * 60)
    print(f"Summary: Created {len(created)}, Existing {len(existing)}, Errors {len(errors)}")
    print("-" * 60 + "\n")
    
    return summary


def delete_roles():
    """
    Delete all COMS custom roles.
    Use with caution - for development/testing only.
    
    Returns:
        dict: Summary of deleted roles
    """
    deleted = []
    errors = []
    
    print("\n" + "=" * 60)
    print("COMS Phase S1: Deleting Roles (DEVELOPMENT ONLY)")
    print("=" * 60 + "\n")
    
    for role_data in COMS_ROLES:
        role_name = role_data["role_name"]
        
        try:
            if frappe.db.exists("Role", role_name):
                # Check if role has users
                user_count = frappe.db.count("Has Role", {"role": role_name})
                
                if user_count > 0:
                    print(f"  ⚠ Role {role_name} has {user_count} users assigned")
                    # Remove role from users first
                    frappe.db.delete("Has Role", {"role": role_name})
                    print(f"    → Removed role from {user_count} users")
                
                # Delete permissions first
                frappe.db.delete("DocPerm", {"role": role_name})
                frappe.db.delete("Custom DocPerm", {"role": role_name})
                
                # Delete the role
                frappe.delete_doc("Role", role_name, ignore_permissions=True)
                print(f"  ✓ Deleted role: {role_name}")
                deleted.append(role_name)
            else:
                print(f"  ○ Role doesn't exist: {role_name}")
                
        except Exception as e:
            error_msg = f"Error deleting role {role_name}: {str(e)}"
            print(f"  ✗ {error_msg}")
            errors.append(error_msg)
    
    frappe.db.commit()
    
    print("\n" + "-" * 60)
    print(f"Deleted: {len(deleted)}, Errors: {len(errors)}")
    print("-" * 60 + "\n")
    
    return {"deleted": deleted, "errors": errors}


def verify_roles():
    """
    Verify that all COMS roles are properly configured.
    
    Returns:
        dict: Verification results
    """
    results = []
    all_valid = True
    
    print("\n" + "=" * 60)
    print("COMS Phase S1: Verifying Roles")
    print("=" * 60 + "\n")
    
    for role_data in COMS_ROLES:
        role_name = role_data["role_name"]
        role_result = {
            "role": role_name,
            "exists": False,
            "desk_access_correct": False,
            "user_count": 0
        }
        
        if frappe.db.exists("Role", role_name):
            role = frappe.get_doc("Role", role_name)
            role_result["exists"] = True
            role_result["desk_access_correct"] = role.desk_access == role_data["desk_access"]
            role_result["user_count"] = frappe.db.count("Has Role", {"role": role_name})
            
            if role_result["desk_access_correct"]:
                status = "✓"
            else:
                status = "⚠"
                all_valid = False
                
            print(f"  {status} {role_name}")
            print(f"      Desk Access: {role.desk_access} (expected: {role_data['desk_access']})")
            print(f"      Users: {role_result['user_count']}")
        else:
            print(f"  ✗ {role_name} - NOT FOUND")
            all_valid = False
        
        results.append(role_result)
    
    print("\n" + "-" * 60)
    print(f"Overall: {'✓ All roles configured correctly' if all_valid else '✗ Some issues found'}")
    print("-" * 60 + "\n")
    
    return {
        "results": results,
        "all_valid": all_valid
    }


def assign_role_to_user(user, role_name):
    """
    Assign a COMS role to a user.
    
    Args:
        user: Username
        role_name: One of the COMS roles
        
    Returns:
        bool: Success status
    """
    valid_roles = [r["role_name"] for r in COMS_ROLES]
    
    if role_name not in valid_roles:
        frappe.throw(_("Invalid COMS role: {0}. Valid roles: {1}").format(
            role_name, ", ".join(valid_roles)
        ))
    
    if not frappe.db.exists("User", user):
        frappe.throw(_("User {0} not found").format(user))
    
    if not frappe.db.exists("Role", role_name):
        frappe.throw(_("Role {0} not found. Run s1_create_roles first.").format(role_name))
    
    # Check if already has role
    if frappe.db.exists("Has Role", {"parent": user, "role": role_name}):
        print(f"User {user} already has role {role_name}")
        return True
    
    # Assign role
    user_doc = frappe.get_doc("User", user)
    user_doc.append("roles", {"role": role_name})
    user_doc.save(ignore_permissions=True)
    
    print(f"Assigned role {role_name} to user {user}")
    frappe.db.commit()
    
    return True


def execute():
    """
    Main execution function for bench execute command.
    """
    return create_roles()


if __name__ == "__main__":
    execute()
