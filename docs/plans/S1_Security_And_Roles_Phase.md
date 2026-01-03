# Phase S1: Security & Roles Implementation Plan

**Document Version:** 1.0  
**Created:** 2025-12-30  
**Status:** Planning  
**Objective:** Establish the foundational security layer and role-based access controls that will enable the separation of the Consultant Portal from the Core ERPNext Desk.

---

## PART 1: COMPLETE CURRENT SYSTEM STRUCTURE

This section provides a comprehensive inventory of the existing COMS implementation before separation activities begin.

### 1.1 Application Root

```
d:\erpnext\coms\
├── __init__.py                              # App package initialization
├── hooks.py                                 # Central configuration (2.88 KB)
│                                             - doc_events
│                                             - fixtures
│                                             - scheduler_events
│                                             - required_apps: ["erpnext"]
└── consulting\                              # Main Module (Consulting)
```

### 1.2 Consulting Module Structure

```
d:\erpnext\coms\consulting\
├── __init__.py
│
├── doctype\                                 # 10 Custom Doctypes
│   ├── __init__.py
│   ├── client_contract\                     # Standard Doctype
│   │   ├── __init__.py
│   │   ├── client_contract.json             (9.5 KB)
│   │   ├── client_contract.py               (4.1 KB)
│   │   └── client_contract.js               (3.1 KB)
│   │
│   ├── consultant_contract\                 # Standard Doctype
│   │   ├── __init__.py
│   │   ├── consultant_contract.json
│   │   └── consultant_contract.py
│   │
│   ├── deliverable\                         # Submittable Doctype
│   │   ├── __init__.py
│   │   ├── deliverable.json                 (9.0 KB)
│   │   ├── deliverable.py                   (5.9 KB)
│   │   └── deliverable.js                   (4.2 KB)
│   │
│   ├── expertise_area\                      # Standard Doctype
│   │   ├── __init__.py
│   │   ├── expertise_area.json              (2.3 KB)
│   │   └── expertise_area.py
│   │
│   ├── contract_milestone\                  # Child Table
│   │   ├── __init__.py
│   │   └── contract_milestone.json
│   │
│   ├── contract_project\                    # Child Table
│   │   ├── __init__.py
│   │   └── contract_project.json
│   │
│   ├── consultant_project_assignment\       # Child Table
│   │   ├── __init__.py
│   │   └── consultant_project_assignment.json
│   │
│   ├── consultant_expertise\                # Child Table
│   │   ├── __init__.py
│   │   └── consultant_expertise.json
│   │
│   ├── deliverable_revision\                # Child Table
│   │   ├── __init__.py
│   │   └── deliverable_revision.json
│   │
│   └── project_consultant\                  # Child Table
│       ├── __init__.py
│       ├── project_consultant.json          (3.0 KB)
│       └── project_consultant.py
│
├── events\                                  # Event Handlers (5 files)
│   ├── __init__.py
│   ├── project_events.py                    (3.3 KB) - validate_project, on_project_update
│   ├── task_events.py                       (5.5 KB) - validate_task, on_task_update, on_task_before_save
│   ├── timesheet_events.py                  (6.0 KB) - on_timesheet_validate, on_timesheet_submit, on_timesheet_cancel
│   ├── invoice_events.py                    (5.0 KB) - update_contract_invoiced, revert_contract_invoiced
│   └── deliverable_events.py                (3.1 KB) - on_deliverable_validate, on_deliverable_update, send_overdue_alerts
│
├── billing\                                 # Billing Logic (4 files)
│   ├── __init__.py
│   ├── invoice_generator.py                 (13.5 KB) - ConsultingInvoiceGenerator class
│   ├── milestone_billing.py                 (8.9 KB)  - MilestoneBillingHandler class
│   ├── profitability.py                     (6.1 KB)  - ProjectProfitabilityCalculator class
│   └── scheduled_tasks.py                   (2.7 KB)  - remind_unbilled_time, generate_weekly_invoices
│
├── report\                                  # 6 Custom Reports
│   ├── __init__.py
│   ├── consultant_utilization_report\       (4 files: .py, .js, .json, __init__.py)
│   ├── project_profitability_report\        (4 files)
│   ├── client_billing_summary\              (4 files)
│   ├── time_entry_summary\                  (4 files)
│   ├── deliverable_status_report\           (4 files)
│   └── contract_compliance_report\          (4 files)
│
├── invoice_generator.py                     # (Duplicate - 13.5 KB)
├── milestone_billing.py                     # (Duplicate - 8.9 KB)
├── profitability.py                         # (Duplicate - 6.1 KB)
└── scheduled_tasks.py                       # (Duplicate - 2.7 KB)
```

### 1.3 Integration Points with Core ERPNext

| ERPNext Doctype | Integration Method | Integration File |
|-----------------|-------------------|------------------|
| **Employee** | Custom Fields (7) | Fixtures: `consultant_type`, `hourly_rate`, `expertise_areas`, etc. |
| **Customer** | Custom Fields (4) | Fixtures: `organization_type`, `client_classification`, etc. |
| **Project** | Custom Fields (8) + Events | `project_events.py` + Fixtures |
| **Task** | Custom Fields (7) + Events + Workflow | `task_events.py` + `Consulting Task Workflow` |
| **Timesheet** | Custom Fields (6) + Events | `timesheet_events.py` |
| **Sales Invoice** | Custom Fields (7) + Events | `invoice_events.py` |

---

## PART 2: PHASE S1 SCOPE - FILES TO BE CREATED/MODIFIED

### 2.1 New Files to Create

| # | File Path | Purpose | Size Est. |
|---|-----------|---------|-----------|
| 1 | `d:\erpnext\coms\consulting\security\__init__.py` | Package initialization | <1 KB |
| 2 | `d:\erpnext\coms\consulting\security\roles.py` | Role definition logic | ~3 KB |
| 3 | `d:\erpnext\coms\consulting\security\permissions.py` | Permission matrix logic | ~5 KB |
| 4 | `d:\erpnext\coms\consulting\security\row_level_security.py` | Document ownership filters | ~4 KB |
| 5 | `d:\erpnext\coms\consulting\doctype\consultant_role\consultant_role.json` | Custom Role Definition Doctype | ~2 KB |
| 6 | `d:\erpnext\coms\consulting\doctype\consultant_role\consultant_role.py` | Role logic | ~2 KB |
| 7 | `d:\erpnext\coms\consulting\doctype\consultant_role\__init__.py` | Package init | <1 KB |
| 8 | `d:\erpnext\coms\consulting\api\__init__.py` | API package initialization | <1 KB |
| 9 | `d:\erpnext\coms\consulting\api\consultant_api.py` | Whitelisted API endpoints for consultants | ~6 KB |
| 10 | `d:\erpnext\coms_setup_files\phase_scripts\s1_create_roles.py` | Setup script to create roles in database | ~4 KB |
| 11 | `d:\erpnext\coms_setup_files\phase_scripts\s1_apply_permissions.py` | Setup script to apply permission rules | ~5 KB |

### 2.2 Files to Modify

| # | File Path | Modification |
|---|-----------|--------------|
| 1 | `d:\erpnext\coms\hooks.py` | Add `has_permission` hooks, add role fixtures |
| 2 | `d:\erpnext\coms\consulting\doctype\client_contract\client_contract.json` | Add role-based permissions |
| 3 | `d:\erpnext\coms\consulting\doctype\consultant_contract\consultant_contract.json` | Add role-based permissions |
| 4 | `d:\erpnext\coms\consulting\doctype\deliverable\deliverable.json` | Add role-based permissions |

---

## PART 3: DETAILED IMPLEMENTATION PLAN

### 3.1 Step 1 - Define Custom Roles

**Objective:** Create three new roles that will govern access in the separated system.

#### Roles to Create:

| Role Name | Role Type | Description |
|-----------|-----------|-------------|
| `Consultant` | Portal User | Can view/edit own tasks, timesheets, deliverables |
| `Consulting Partner` | Portal Manager | Can view all project data, approve deliverables |
| `Consulting Admin` | System User | Full access to COMS module, can assign consultants |

#### Implementation File: `d:\erpnext\coms_setup_files\phase_scripts\s1_create_roles.py`

```python
# Role creation script - to be executed via bench console

import frappe

COMS_ROLES = [
    {
        "role_name": "Consultant",
        "desk_access": 0,  # Portal only
        "is_custom": 1,
        "description": "External or internal consultant with limited access"
    },
    {
        "role_name": "Consulting Partner",
        "desk_access": 1,  # Desk access for management
        "is_custom": 1,
        "description": "Senior consultant or partner with managerial access"
    },
    {
        "role_name": "Consulting Admin",
        "desk_access": 1,
        "is_custom": 1,
        "description": "Full COMS administrative access"
    }
]

def create_roles():
    for role_data in COMS_ROLES:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.new_doc("Role")
            role.role_name = role_data["role_name"]
            role.desk_access = role_data["desk_access"]
            role.is_custom = role_data["is_custom"]
            role.insert(ignore_permissions=True)
            print(f"Created role: {role_data['role_name']}")
        else:
            print(f"Role already exists: {role_data['role_name']}")
    frappe.db.commit()

if __name__ == "__main__":
    create_roles()
```

---

### 3.2 Step 2 - Define Permission Matrix

**Objective:** Establish what each role can do on each doctype.

#### Permission Matrix:

| Doctype | Consultant | Consulting Partner | Consulting Admin |
|---------|------------|-------------------|------------------|
| **Client Contract** | Read (own projects) | Read/Write | Full |
| **Consultant Contract** | Read (own) | Read | Full |
| **Project** | Read (assigned) | Read/Write | Full |
| **Task** | Read/Write (assigned) | Read/Write | Full |
| **Timesheet** | Create/Read/Write (own) | Read (team) | Full |
| **Deliverable** | Create/Submit (own) | Approve/Reject | Full |
| **Sales Invoice** | None | Read (own projects) | Full |
| **Employee** | Read (own profile) | Read (team) | Read |
| **Customer** | None | Read | Full |

#### Implementation File: `d:\erpnext\coms\consulting\security\permissions.py`

```python
# Permission configuration for COMS roles

PERMISSION_MATRIX = {
    "Client Contract": {
        "Consultant": {"read": 1, "if_owner": 0},  # Via linked projects only
        "Consulting Partner": {"read": 1, "write": 1, "create": 0},
        "Consulting Admin": {"read": 1, "write": 1, "create": 1, "delete": 1}
    },
    "Consultant Contract": {
        "Consultant": {"read": 1, "if_owner": 1},
        "Consulting Partner": {"read": 1},
        "Consulting Admin": {"read": 1, "write": 1, "create": 1, "delete": 1}
    },
    "Deliverable": {
        "Consultant": {"read": 1, "write": 1, "create": 1, "submit": 1, "if_owner": 1},
        "Consulting Partner": {"read": 1, "write": 1, "submit": 1, "cancel": 1},
        "Consulting Admin": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1}
    },
    "Timesheet": {
        "Consultant": {"read": 1, "write": 1, "create": 1, "submit": 1, "if_owner": 1},
        "Consulting Partner": {"read": 1},
        "Consulting Admin": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1}
    }
}

def get_permissions_for_role(doctype, role):
    """Get permission dict for a specific doctype and role"""
    return PERMISSION_MATRIX.get(doctype, {}).get(role, {})
```

---

### 3.3 Step 3 - Implement Row-Level Security

**Objective:** Consultants should only see data related to their assigned projects.

#### Implementation File: `d:\erpnext\coms\consulting\security\row_level_security.py`

```python
# Row-level security filters for COMS

import frappe

def get_consultant_employee_id():
    """Get the Employee ID linked to the current user"""
    return frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")

def get_consultant_projects():
    """Get list of projects where current user is a consultant"""
    employee_id = get_consultant_employee_id()
    if not employee_id:
        return []
    
    # Get from Project Consultant child table
    projects = frappe.db.sql("""
        SELECT DISTINCT parent as project
        FROM `tabProject Consultant`
        WHERE consultant = %s
    """, (employee_id,), as_dict=True)
    
    return [p.project for p in projects]

def apply_project_filter(user):
    """Permission query for Project doctype"""
    if "Consulting Admin" in frappe.get_roles(user):
        return ""  # No filter for admins
    
    projects = get_consultant_projects()
    if not projects:
        return "1=0"  # No access if not assigned to any project
    
    project_list = ", ".join([f"'{p}'" for p in projects])
    return f"`tabProject`.name IN ({project_list})"

def apply_task_filter(user):
    """Permission query for Task doctype"""
    if "Consulting Admin" in frappe.get_roles(user):
        return ""
    
    employee_id = get_consultant_employee_id()
    if not employee_id:
        return "1=0"
    
    # Tasks where user is assigned consultant OR task is in their project
    projects = get_consultant_projects()
    project_list = ", ".join([f"'{p}'" for p in projects]) if projects else "''"
    
    return f"""
        (`tabTask`.assigned_consultant = '{employee_id}'
         OR `tabTask`.project IN ({project_list}))
    """

def apply_deliverable_filter(user):
    """Permission query for Deliverable doctype"""
    if "Consulting Admin" in frappe.get_roles(user):
        return ""
    
    employee_id = get_consultant_employee_id()
    projects = get_consultant_projects()
    project_list = ", ".join([f"'{p}'" for p in projects]) if projects else "''"
    
    return f"""
        (`tabDeliverable`.assigned_consultant = '{employee_id}'
         OR `tabDeliverable`.project IN ({project_list}))
    """

def apply_timesheet_filter(user):
    """Permission query for Timesheet doctype - only own timesheets"""
    if "Consulting Admin" in frappe.get_roles(user):
        return ""
    
    employee_id = get_consultant_employee_id()
    if not employee_id:
        return "1=0"
    
    return f"`tabTimesheet`.employee = '{employee_id}'"
```

---

### 3.4 Step 4 - Update hooks.py

**Objective:** Register permission queries and permission handlers.

#### Modifications to `d:\erpnext\coms\hooks.py`:

```python
# Add to hooks.py

# Permission Query (Row-Level Security)
permission_query_conditions = {
    "Project": "coms.consulting.security.row_level_security.apply_project_filter",
    "Task": "coms.consulting.security.row_level_security.apply_task_filter",
    "Deliverable": "coms.consulting.security.row_level_security.apply_deliverable_filter",
    "Timesheet": "coms.consulting.security.row_level_security.apply_timesheet_filter"
}

# Has Permission (Document-Level Check)
has_permission = {
    "Project": "coms.consulting.security.row_level_security.has_project_permission",
    "Deliverable": "coms.consulting.security.row_level_security.has_deliverable_permission"
}

# Add roles to fixtures
fixtures = [
    # ... existing fixtures ...
    {
        "dt": "Role",
        "filters": [["name", "in", ["Consultant", "Consulting Partner", "Consulting Admin"]]]
    }
]
```

---

### 3.5 Step 5 - Create Consultant API Endpoints

**Objective:** Provide secure API access for the future Consultant Portal.

#### Implementation File: `d:\erpnext\coms\consulting\api\consultant_api.py`

```python
# Secure API endpoints for Consultant Portal

import frappe
from frappe import _

@frappe.whitelist()
def get_my_dashboard():
    """Get dashboard data for current consultant"""
    employee_id = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    
    if not employee_id:
        frappe.throw(_("No employee record linked to your account"))
    
    # Get assigned projects
    projects = frappe.db.sql("""
        SELECT DISTINCT p.name, p.project_name, p.status, p.percent_complete
        FROM `tabProject` p
        INNER JOIN `tabProject Consultant` pc ON pc.parent = p.name
        WHERE pc.consultant = %s AND p.status = 'Open'
    """, (employee_id,), as_dict=True)
    
    # Get pending tasks
    pending_tasks = frappe.db.count("Task", {
        "assigned_consultant": employee_id,
        "status": ["not in", ["Completed", "Cancelled"]]
    })
    
    # Get pending deliverables
    pending_deliverables = frappe.db.count("Deliverable", {
        "assigned_consultant": employee_id,
        "status": ["not in", ["Final", "Cancelled", "Approved"]]
    })
    
    # Get this month's timesheet hours
    from frappe.utils import get_first_day, today
    month_start = get_first_day(today())
    
    hours_logged = frappe.db.sql("""
        SELECT COALESCE(SUM(total_hours), 0) as hours
        FROM `tabTimesheet`
        WHERE employee = %s AND start_date >= %s AND docstatus = 1
    """, (employee_id, month_start), as_dict=True)[0].hours
    
    return {
        "employee_id": employee_id,
        "active_projects": len(projects),
        "projects": projects,
        "pending_tasks": pending_tasks,
        "pending_deliverables": pending_deliverables,
        "hours_this_month": hours_logged
    }

@frappe.whitelist()
def get_my_tasks(project=None, status=None):
    """Get tasks assigned to current consultant"""
    employee_id = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    
    filters = {"assigned_consultant": employee_id}
    if project:
        filters["project"] = project
    if status:
        filters["status"] = status
    else:
        filters["status"] = ["not in", ["Completed", "Cancelled"]]
    
    return frappe.get_all("Task", filters=filters, fields=[
        "name", "subject", "project", "status", "priority",
        "exp_start_date", "exp_end_date", "progress"
    ], order_by="exp_end_date asc")

@frappe.whitelist()
def get_my_timesheets(limit=10):
    """Get timesheets for current consultant"""
    employee_id = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    
    return frappe.get_all("Timesheet", 
        filters={"employee": employee_id},
        fields=["name", "start_date", "end_date", "total_hours", "status", "docstatus"],
        order_by="start_date desc",
        limit=limit
    )
```

---

## PART 4: VERIFICATION CHECKLIST

### 4.1 Role Creation Verification
- [ ] Role "Consultant" exists in the system
- [ ] Role "Consulting Partner" exists in the system
- [ ] Role "Consulting Admin" exists in the system
- [ ] Consultant role has `desk_access = 0`
- [ ] Partner and Admin roles have `desk_access = 1`

### 4.2 Permission Verification
- [ ] Consultant cannot access Customer doctype
- [ ] Consultant can only see own timesheets
- [ ] Consultant can only see assigned tasks
- [ ] Consulting Partner can see all project data
- [ ] Consulting Admin has full access

### 4.3 API Verification
- [ ] `/api/method/coms.consulting.api.consultant_api.get_my_dashboard` returns data
- [ ] API returns only data for logged-in consultant
- [ ] Unauthorized users get permission error

---

## PART 5: NEXT PHASE PREPARATION

Upon successful completion of Phase S1:
1. All security infrastructure will be in place
2. We can proceed to **Phase S2: Portal Architecture** to build the consultant-facing interface
3. The API endpoints created here will serve the Portal views

---

**End of Phase S1 Plan**
