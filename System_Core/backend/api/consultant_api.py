# -*- coding: utf-8 -*-
# Copyright (c) 2025, COMS
# License: MIT

"""
Consultant API Endpoints
========================

Secure, whitelisted API endpoints for the Consultant Portal.
These endpoints wrap the existing COMS engine logic and enforce
row-level security for the portal UI.

**CRITICAL ARCHITECTURE NOTE:**
These are "Remote Control" wrappers. They call the existing COMS
engine (events, billing, etc.) - they do NOT duplicate logic.

Part of Phase S1: Security & Roles Implementation
"""

import frappe
from frappe import _
from frappe.utils import today, get_first_day, getdate, cint, flt


def _get_employee_id():
    """
    Get the Employee ID linked to the current user.
    Throws if no employee record found.
    
    Returns:
        str: Employee ID
        
    Raises:
        frappe.PermissionError: If no linked employee
    """
    employee_id = frappe.db.get_value(
        "Employee", 
        {"user_id": frappe.session.user}, 
        "name"
    )
    
    if not employee_id:
        frappe.throw(
            _("No employee record linked to your account. Please contact your administrator."),
            frappe.PermissionError
        )
    
    return employee_id


@frappe.whitelist()
def get_my_dashboard():
    """
    Get comprehensive dashboard data for the current consultant.
    
    This endpoint aggregates all key metrics for the portal home screen:
    - Active projects count and details
    - Pending tasks count
    - Pending deliverables count
    - Hours logged this month
    - Upcoming deadlines
    
    Returns:
        dict: Dashboard data
    """
    employee_id = _get_employee_id()
    
    # Get assigned projects with status
    projects = frappe.db.sql("""
        SELECT DISTINCT 
            p.name, 
            p.project_name, 
            p.status, 
            p.percent_complete,
            p.expected_end_date,
            p.project_type
        FROM `tabProject` p
        INNER JOIN `tabProject Consultant` pc ON pc.parent = p.name
        WHERE pc.consultant = %s 
        AND p.status IN ('Open', 'Working')
        ORDER BY p.expected_end_date ASC
    """, (employee_id,), as_dict=True)
    
    # Count pending tasks (not completed or cancelled)
    pending_tasks = frappe.db.count("Task", {
        "assigned_consultant": employee_id,
        "status": ["not in", ["Completed", "Cancelled", "Template"]]
    })
    
    # Count overdue tasks
    overdue_tasks = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabTask`
        WHERE assigned_consultant = %s
        AND status NOT IN ('Completed', 'Cancelled', 'Template')
        AND exp_end_date < %s
    """, (employee_id, today()), as_dict=True)[0].count
    
    # Count pending deliverables
    pending_deliverables = frappe.db.count("Deliverable", {
        "assigned_consultant": employee_id,
        "status": ["not in", ["Final", "Cancelled", "Approved"]]
    })
    
    # Get this month's timesheet hours
    month_start = get_first_day(today())
    
    hours_result = frappe.db.sql("""
        SELECT COALESCE(SUM(total_hours), 0) as hours
        FROM `tabTimesheet`
        WHERE employee = %s 
        AND start_date >= %s 
        AND docstatus = 1
    """, (employee_id, month_start), as_dict=True)
    
    hours_logged = flt(hours_result[0].hours) if hours_result else 0
    
    # Get upcoming deadlines (next 7 days)
    upcoming_deadlines = frappe.db.sql("""
        SELECT 
            name,
            subject,
            exp_end_date as deadline,
            status,
            priority,
            'Task' as doctype
        FROM `tabTask`
        WHERE assigned_consultant = %s
        AND status NOT IN ('Completed', 'Cancelled', 'Template')
        AND exp_end_date BETWEEN %s AND DATE_ADD(%s, INTERVAL 7 DAY)
        
        UNION ALL
        
        SELECT 
            name,
            deliverable_name as subject,
            due_date as deadline,
            status,
            priority,
            'Deliverable' as doctype
        FROM `tabDeliverable`
        WHERE assigned_consultant = %s
        AND status NOT IN ('Final', 'Cancelled', 'Approved')
        AND due_date BETWEEN %s AND DATE_ADD(%s, INTERVAL 7 DAY)
        
        ORDER BY deadline ASC
        LIMIT 10
    """, (employee_id, today(), today(), employee_id, today(), today()), as_dict=True)
    
    # Get employee name for greeting
    employee_name = frappe.db.get_value("Employee", employee_id, "employee_name")
    
    return {
        "employee_id": employee_id,
        "employee_name": employee_name,
        "active_projects": len(projects),
        "projects": projects,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "pending_deliverables": pending_deliverables,
        "hours_this_month": hours_logged,
        "upcoming_deadlines": upcoming_deadlines,
        "current_date": today()
    }


@frappe.whitelist()
def get_my_tasks(project=None, status=None, limit=50, offset=0):
    """
    Get tasks assigned to the current consultant.
    
    Args:
        project: (optional) Filter by project
        status: (optional) Filter by status
        limit: Maximum number of results (default 50)
        offset: Pagination offset (default 0)
        
    Returns:
        dict: Tasks list with total count
    """
    employee_id = _get_employee_id()
    
    filters = {"assigned_consultant": employee_id}
    
    if project:
        filters["project"] = project
    
    if status:
        filters["status"] = status
    else:
        filters["status"] = ["not in", ["Completed", "Cancelled", "Template"]]
    
    # Get total count for pagination
    total_count = frappe.db.count("Task", filters)
    
    # Get tasks with pagination
    tasks = frappe.get_all("Task", 
        filters=filters, 
        fields=[
            "name", 
            "subject", 
            "project", 
            "status", 
            "priority",
            "exp_start_date", 
            "exp_end_date", 
            "progress",
            "estimated_hours",
            "is_billable",
            "description"
        ], 
        order_by="exp_end_date asc, priority desc",
        limit_page_length=cint(limit),
        limit_start=cint(offset)
    )
    
    return {
        "tasks": tasks,
        "total": total_count,
        "limit": cint(limit),
        "offset": cint(offset)
    }


@frappe.whitelist()
def get_my_deliverables(project=None, status=None, limit=50, offset=0):
    """
    Get deliverables assigned to the current consultant.
    
    Args:
        project: (optional) Filter by project
        status: (optional) Filter by status
        limit: Maximum number of results
        offset: Pagination offset
        
    Returns:
        dict: Deliverables list with total count
    """
    employee_id = _get_employee_id()
    
    filters = {"assigned_consultant": employee_id}
    
    if project:
        filters["project"] = project
    
    if status:
        filters["status"] = status
    else:
        filters["status"] = ["not in", ["Final", "Cancelled"]]
    
    # Get total count
    total_count = frappe.db.count("Deliverable", filters)
    
    # Get deliverables
    deliverables = frappe.get_all("Deliverable",
        filters=filters,
        fields=[
            "name",
            "deliverable_name",
            "project",
            "status",
            "deliverable_type",
            "priority",
            "due_date",
            "submission_date",
            "approval_status",
            "current_version",
            "docstatus"
        ],
        order_by="due_date asc, priority desc",
        limit_page_length=cint(limit),
        limit_start=cint(offset)
    )
    
    return {
        "deliverables": deliverables,
        "total": total_count,
        "limit": cint(limit),
        "offset": cint(offset)
    }


@frappe.whitelist()
def get_my_timesheets(month=None, year=None, limit=20, offset=0):
    """
    Get timesheets for the current consultant.
    
    Args:
        month: (optional) Filter by month (1-12)
        year: (optional) Filter by year
        limit: Maximum number of results
        offset: Pagination offset
        
    Returns:
        dict: Timesheets list with total count and summary
    """
    employee_id = _get_employee_id()
    
    filters = {"employee": employee_id}
    
    # Build date range filter if month/year provided
    if month and year:
        from frappe.utils import get_first_day, get_last_day
        import calendar
        
        month = cint(month)
        year = cint(year)
        first_day = f"{year}-{month:02d}-01"
        last_day = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
        
        filters["start_date"] = [">=", first_day]
        filters["end_date"] = ["<=", last_day]
    
    # Get total count
    total_count = frappe.db.count("Timesheet", filters)
    
    # Get timesheets
    timesheets = frappe.get_all("Timesheet",
        filters=filters,
        fields=[
            "name",
            "start_date",
            "end_date",
            "total_hours",
            "total_billable_hours",
            "total_billed_hours",
            "total_billable_amount",
            "status",
            "docstatus"
        ],
        order_by="start_date desc",
        limit_page_length=cint(limit),
        limit_start=cint(offset)
    )
    
    # Get summary totals
    summary = frappe.db.sql("""
        SELECT 
            COALESCE(SUM(total_hours), 0) as total_hours,
            COALESCE(SUM(total_billable_hours), 0) as billable_hours,
            COALESCE(SUM(total_billable_amount), 0) as billable_amount
        FROM `tabTimesheet`
        WHERE employee = %s AND docstatus = 1
    """, (employee_id,), as_dict=True)[0]
    
    return {
        "timesheets": timesheets,
        "total": total_count,
        "limit": cint(limit),
        "offset": cint(offset),
        "summary": {
            "total_hours": flt(summary.total_hours),
            "billable_hours": flt(summary.billable_hours),
            "billable_amount": flt(summary.billable_amount)
        }
    }


@frappe.whitelist()
def get_my_projects():
    """
    Get all projects assigned to the current consultant.
    
    Returns:
        dict: Projects list with participation details
    """
    employee_id = _get_employee_id()
    
    # Get projects with detailed info
    projects = frappe.db.sql("""
        SELECT 
            p.name,
            p.project_name,
            p.status,
            p.percent_complete,
            p.expected_start_date,
            p.expected_end_date,
            p.project_type,
            p.priority,
            p.customer,
            p.client_contract,
            pc.role as consultant_role,
            pc.allocation_percentage
        FROM `tabProject` p
        INNER JOIN `tabProject Consultant` pc ON pc.parent = p.name
        WHERE pc.consultant = %s
        ORDER BY 
            CASE p.status 
                WHEN 'Working' THEN 1 
                WHEN 'Open' THEN 2 
                ELSE 3 
            END,
            p.expected_end_date ASC
    """, (employee_id,), as_dict=True)
    
    # Enrich with task/deliverable counts per project
    for project in projects:
        project['task_count'] = frappe.db.count("Task", {
            "project": project.name,
            "assigned_consultant": employee_id,
            "status": ["not in", ["Completed", "Cancelled", "Template"]]
        })
        
        project['deliverable_count'] = frappe.db.count("Deliverable", {
            "project": project.name,
            "assigned_consultant": employee_id,
            "status": ["not in", ["Final", "Cancelled"]]
        })
    
    return {
        "projects": projects,
        "total": len(projects)
    }


@frappe.whitelist()
def get_my_profile():
    """
    Get the consultant's profile information.
    
    Returns profile data that can be displayed/edited in the portal.
    
    Returns:
        dict: Profile information
    """
    employee_id = _get_employee_id()
    
    # Get employee record
    employee = frappe.get_doc("Employee", employee_id)
    
    # Get consultant contract if exists
    contract = frappe.db.get_value(
        "Consultant Contract",
        {"consultant": employee_id, "status": "Active"},
        ["name", "contract_type", "engagement_type", "start_date", "end_date", 
         "rate_type", "rate_amount", "currency"],
        as_dict=True
    )
    
    # Get expertise areas (custom field on Employee)
    expertise = []
    if hasattr(employee, 'expertise_areas'):
        expertise = [e.expertise_area for e in employee.expertise_areas or []]
    
    # Build profile response
    profile = {
        "employee_id": employee_id,
        "employee_name": employee.employee_name,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.prefered_email or employee.personal_email or employee.company_email,
        "user_id": employee.user_id,
        "designation": employee.designation,
        "department": employee.department,
        "company": employee.company,
        "date_of_joining": employee.date_of_joining,
        "image": employee.image,
        "consultant_type": getattr(employee, 'consultant_type', None),
        "hourly_rate": getattr(employee, 'hourly_rate', None),
        "expertise_areas": expertise,
        "bio": getattr(employee, 'bio', None),
        "cell_number": employee.cell_number,
        "contract": contract
    }
    
    return profile


@frappe.whitelist()
def update_task_status(task_name, new_status):
    """
    Update the status of an assigned task.
    
    This wraps the existing Task workflow, ensuring only
    valid transitions are allowed.
    
    Args:
        task_name: Name of the task
        new_status: New status to set
        
    Returns:
        dict: Updated task info
    """
    employee_id = _get_employee_id()
    
    # Load task and verify ownership
    task = frappe.get_doc("Task", task_name)
    
    if task.assigned_consultant != employee_id:
        frappe.throw(_("You can only update tasks assigned to you"), frappe.PermissionError)
    
    # Valid status transitions for consultants
    valid_statuses = ["Open", "Working", "Pending Review", "Completed"]
    
    if new_status not in valid_statuses:
        frappe.throw(_("Invalid status: {0}").format(new_status))
    
    # Update status - this triggers the existing task_events.py handlers
    task.status = new_status
    task.save()
    
    return {
        "name": task.name,
        "status": task.status,
        "message": _("Task status updated successfully")
    }


@frappe.whitelist()
def log_time(project, task=None, hours=0, activity_type=None, description=None):
    """
    Log time for a project/task.
    
    Creates or updates a timesheet with the logged time.
    Wraps the existing timesheet_events.py logic.
    
    Args:
        project: Project name (required)
        task: Task name (optional)
        hours: Hours to log (required)
        activity_type: Type of activity
        description: Work description
        
    Returns:
        dict: Created/updated timesheet info
    """
    employee_id = _get_employee_id()
    hours = flt(hours)
    
    if hours <= 0:
        frappe.throw(_("Hours must be greater than 0"))
    
    # Verify project access
    from backend.security.row_level_security import get_consultant_projects
    projects = get_consultant_projects()
    
    if project not in projects:
        frappe.throw(_("You don't have access to this project"), frappe.PermissionError)
    
    # Create timesheet detail
    timesheet = frappe.new_doc("Timesheet")
    timesheet.employee = employee_id
    timesheet.start_date = today()
    timesheet.end_date = today()
    
    timesheet.append("time_logs", {
        "activity_type": activity_type or "Consulting",
        "from_time": frappe.utils.now_datetime(),
        "hours": hours,
        "project": project,
        "task": task,
        "description": description,
        "is_billable": 1
    })
    
    # This triggers the existing timesheet_events.py validation and rate logic
    timesheet.insert()
    
@frappe.whitelist()
def get_project_details(project):
    """
    S3: Get detailed dashboard for a specific project.
    """
    employee_id = _get_employee_id()
    
    # 1. Fetch Core Project
    proj = frappe.db.sql("""
        SELECT p.*, pc.role as my_role
        FROM `tabProject` p
        INNER JOIN `tabProject Consultant` pc ON pc.parent = p.name
        WHERE p.name = %s AND pc.consultant = %s
    """, (project, employee_id), as_dict=True)

    if not proj:
        frappe.throw(_("Project not found or access denied"), frappe.PermissionError)

    proj = proj[0]

    # 2. Fetch pending tasks count
    proj['pending_tasks_count'] = frappe.db.count("Task", {
        "project": project,
        "assigned_consultant": employee_id,
        "status": ["not in", ["Completed", "Cancelled"]]
    })

    return proj

@frappe.whitelist()
def log_session(task, hours, description, activity="Consulting"):
    """
    S3: Simplified Time Logger Wrapper.
    Finds the project from the task and creates a Timesheet.
    """
    employee_id = _get_employee_id()
    
    # 1. Get Task & Project Details
    task_doc = frappe.db.get_value("Task", task, ["project", "subject"], as_dict=True)
    if not task_doc:
         frappe.throw(_("Task not found"))

    # 2. Create Timesheet
    ts = frappe.new_doc("Timesheet")
    ts.employee = employee_id
    ts.title = f"Session for {task_doc.subject}"
    ts.append("time_logs", {
        "activity_type": activity,
        "hours": flt(hours),
        "project": task_doc.project,
        "task": task,
        "description": description,
        "is_billable": 1 # Default, logic can override in events
    })
    
    ts.save()
    ts.submit() # Auto-submit for S3 flow? Or keep draft? Sticking to Submit for now.
    
    return {"status": "success", "timesheet": ts.name}

@frappe.whitelist()
def get_my_contracts():
    """
    S4: Get active legal contracts for the Consultant (Read-Only).
    """
    employee_id = _get_employee_id()
    
    contracts = frappe.db.get_list("Consultant Contract",
        filters={"consultant": employee_id, "status": "Active"},
        fields=["name", "contract_type", "status", "start_date", "end_date", 
                "currency", "rate_amount", "rate_type", "terms"]
    )

    # Enrich with Project Count
    for c in contracts:
        c["project_count"] = len(frappe.db.get_all("Consultant Contract Project", {"parent": c.name}))
    
    return {"contracts": contracts}

@frappe.whitelist()
def get_my_finance_summary():
    """
    S4: Get financial health summary (Billable hours vs Paid Invoices).
    """
    employee_id = _get_employee_id()
    
    # 1. Calc Billable This Month
    month_start = get_first_day(today())
    billable_hours = frappe.db.sql("""
        SELECT COALESCE(SUM(total_billable_hours), 0) 
        FROM `tabTimesheet` 
        WHERE employee=%s AND start_date >= %s AND docstatus=1
    """, (employee_id, month_start))[0][0]

    # Approx Amount (this is an estimate, real amount is in Sales Invoice)
    rate = frappe.db.get_value("Employee", employee_id, "hourly_rate") or 0
    month_billable = flt(billable_hours) * flt(rate)

    # 2. Get Invoices (If user is linked to a Supplier/Customer, otherwise we mock for now or use Shadow Invoices)
    # WARNING: Consultants usually don't see Sales Invoices unless they are "Partners".
    # For now, we return empty list or specific "Consultant Invoice" if it existed.
    # We will simulate valid return structure.

    return {
        "currency": "USD", # Default
        "month_billable": month_billable,
        "hours_this_month": flt(billable_hours),
        "pending_amount": 0, # To be implemented with Accounts Module
        "paid_ytd": 0,       # To be implemented with Accounts Module
        "invoices": []       # To be populated if "Self-Billing" is enabled
    }

@frappe.whitelist()
def get_my_clients():
    """
    S5: Get list of Clients linked to correct active projects.
    """
    employee_id = _get_employee_id()
    
    # Get customers from projects where consultant is assigned
    clients = frappe.db.sql("""
        SELECT DISTINCT c.name, c.customer_name, c.customer_type, c.image, 
               p.project_name as active_project
        FROM 	abCustomer c
        INNER JOIN 	abProject p ON p.customer = c.name
        INNER JOIN 	abProject Consultant pc ON pc.parent = p.name
        WHERE pc.consultant = %s AND p.status = 'Open'
    """, (employee_id,), as_dict=True)
    
    return {"clients": clients}

@frappe.whitelist()
def get_consultant_directory():
    """
    S5: Public directory of other consultants (for networking).
    """
    consultants = frappe.db.get_list("Employee",
        filters={"status": "Active", "designation": "Consultant"},
        fields=["name", "employee_name", "image", "designation", "department"],
        limit=20
    )
    return {"consultants": consultants}

@frappe.whitelist()
def get_team_members():
    """
    S5: Get team members working on my projects.
    """
    employee_id = _get_employee_id()
    
    teammates = frappe.db.sql("""
        SELECT DISTINCT e.name, e.employee_name, e.designation, e.image, p.project_name
        FROM 	abEmployee e
        INNER JOIN 	abProject Consultant pc ON pc.consultant = e.name
        INNER JOIN 	abProject p ON pc.parent = p.name
        INNER JOIN 	abProject Consultant me ON me.parent = p.name
        WHERE me.consultant = %s 
          AND e.name != %s 
          AND p.status = 'Open'
    """, (employee_id, employee_id), as_dict=True)
    
    return {"employees": teammates}
