# -*- coding: utf-8 -*-
# Copyright (c) 2025, COMS
# License: MIT

"""
COMS Permission Matrix
======================

Defines the permission matrix for all COMS-related doctypes.
Maps each doctype to role-based permission configurations.

Permission Keys:
- read: Can view documents
- write: Can modify documents
- create: Can create new documents
- delete: Can delete documents
- submit: Can submit submittable documents
- cancel: Can cancel submitted documents
- amend: Can amend cancelled documents
- report: Can view reports
- export: Can export data
- import: Can import data
- share: Can share documents
- print: Can print documents
- email: Can email documents
- if_owner: Permissions apply only to documents owned by the user

Part of Phase S1: Security & Roles Implementation
"""

import frappe
from frappe import _

# Complete Permission Matrix for COMS Doctypes
PERMISSION_MATRIX = {
    # ═══════════════════════════════════════════════════════════════
    # CUSTOM COMS DOCTYPES
    # ═══════════════════════════════════════════════════════════════
    
    "Client Contract": {
        "Consultant": {
            "read": 1, 
            "report": 1,
            "print": 1,
            "if_owner": 0  # Read via linked projects (row-level security handles this)
        },
        "Consulting Partner": {
            "read": 1, 
            "write": 1, 
            "create": 0,  # Partners cannot create - Admin only
            "report": 1,
            "print": 1,
            "email": 1
        },
        "Consulting Admin": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "delete": 1,
            "report": 1,
            "export": 1,
            "import": 1,
            "share": 1,
            "print": 1,
            "email": 1
        }
    },
    
    "Consultant Contract": {
        "Consultant": {
            "read": 1,
            "print": 1,
            "if_owner": 1  # Can only see own contract
        },
        "Consulting Partner": {
            "read": 1,
            "report": 1,
            "print": 1
        },
        "Consulting Admin": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "delete": 1,
            "report": 1,
            "export": 1,
            "import": 1,
            "share": 1,
            "print": 1,
            "email": 1
        }
    },
    
    "Deliverable": {
        "Consultant": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "submit": 1,
            "report": 1,
            "print": 1,
            "if_owner": 1  # Own deliverables only
        },
        "Consulting Partner": {
            "read": 1, 
            "write": 1, 
            "create": 1,
            "submit": 1, 
            "cancel": 1,  # Can reject/cancel deliverables
            "amend": 1,
            "report": 1,
            "print": 1,
            "email": 1
        },
        "Consulting Admin": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "submit": 1, 
            "cancel": 1,
            "amend": 1,
            "delete": 1,
            "report": 1,
            "export": 1,
            "share": 1,
            "print": 1,
            "email": 1
        }
    },
    
    "Expertise Area": {
        "Consultant": {
            "read": 1
        },
        "Consulting Partner": {
            "read": 1,
            "write": 1,
            "create": 1
        },
        "Consulting Admin": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "delete": 1,
            "export": 1,
            "import": 1
        }
    },
    
    # ═══════════════════════════════════════════════════════════════
    # STANDARD ERPNEXT DOCTYPES (with COMS role access)
    # ═══════════════════════════════════════════════════════════════
    
    "Project": {
        "Consultant": {
            "read": 1,
            "report": 1,
            "if_owner": 0  # Filtered by assignment (row-level security)
        },
        "Consulting Partner": {
            "read": 1, 
            "write": 1,
            "create": 1,
            "report": 1,
            "print": 1
        },
        "Consulting Admin": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "delete": 1,
            "report": 1,
            "export": 1,
            "share": 1,
            "print": 1
        }
    },
    
    "Task": {
        "Consultant": {
            "read": 1, 
            "write": 1,
            "report": 1,
            "if_owner": 0  # Filtered by assignment
        },
        "Consulting Partner": {
            "read": 1, 
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1
        },
        "Consulting Admin": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "delete": 1,
            "report": 1,
            "export": 1,
            "share": 1
        }
    },
    
    "Timesheet": {
        "Consultant": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "submit": 1,
            "report": 1,
            "if_owner": 1  # Own timesheets only
        },
        "Consulting Partner": {
            "read": 1,
            "submit": 1,
            "cancel": 1,  # Can cancel team timesheets
            "report": 1
        },
        "Consulting Admin": {
            "read": 1, 
            "write": 1, 
            "create": 1, 
            "submit": 1, 
            "cancel": 1,
            "amend": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        }
    },
    
    "Sales Invoice": {
        "Consultant": {
            # No direct access to Sales Invoice
        },
        "Consulting Partner": {
            "read": 1,  # Read-only for project invoices
            "report": 1,
            "print": 1
        },
        "Consulting Admin": {
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1,
            "cancel": 1,
            "report": 1,
            "print": 1,
            "email": 1
        }
    },
    
    "Employee": {
        "Consultant": {
            "read": 1,
            "if_owner": 1  # Own profile only
        },
        "Consulting Partner": {
            "read": 1,  # Can see team members
            "report": 1
        },
        "Consulting Admin": {
            "read": 1,
            "write": 1,  # Can update consultant details
            "report": 1
        }
    },
    
    "Customer": {
        "Consultant": {
            # No access to Customer doctype
        },
        "Consulting Partner": {
            "read": 1,
            "report": 1
        },
        "Consulting Admin": {
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "report": 1,
            "export": 1
        }
    }
}


def get_permissions_for_role(doctype, role):
    """
    Get permission dict for a specific doctype and role.
    
    Args:
        doctype: DocType name
        role: Role name
        
    Returns:
        dict: Permission configuration or empty dict
    """
    return PERMISSION_MATRIX.get(doctype, {}).get(role, {})


def get_all_permissions_for_doctype(doctype):
    """
    Get all role permissions for a specific doctype.
    
    Args:
        doctype: DocType name
        
    Returns:
        dict: All role permissions for the doctype
    """
    return PERMISSION_MATRIX.get(doctype, {})


def has_doctype_permission(doctype, permission_type, role):
    """
    Check if a role has a specific permission on a doctype.
    
    Args:
        doctype: DocType name
        permission_type: Permission type (read, write, create, etc.)
        role: Role name
        
    Returns:
        bool: True if permission granted
    """
    perms = get_permissions_for_role(doctype, role)
    return bool(perms.get(permission_type, 0))


def generate_doctype_permissions(doctype):
    """
    Generate permissions array for a doctype JSON.
    Used when updating doctype definitions.
    
    Args:
        doctype: DocType name
        
    Returns:
        list: Permissions array for doctype JSON
    """
    permissions = []
    doctype_perms = PERMISSION_MATRIX.get(doctype, {})
    
    for role, perms in doctype_perms.items():
        if perms:  # Only add if there are permissions defined
            perm_entry = {"role": role}
            perm_entry.update(perms)
            permissions.append(perm_entry)
    
    return permissions


def get_coms_doctypes():
    """
    Get list of all doctypes managed by COMS permissions.
    
    Returns:
        list: DocType names
    """
    return list(PERMISSION_MATRIX.keys())
