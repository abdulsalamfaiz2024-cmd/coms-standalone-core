
app_name = "coms"
app_title = "COMS"
app_publisher = "Your Company"
app_description = "Consulting Operations and Management System"
app_email = "your@email.com"
app_license = "mit"

# Required Apps
required_apps = ["erpnext"]

# App includes
# app_include_css = "/assets/coms/css/coms.css"
# app_include_js = "/assets/coms/js/coms.js"

# Fixtures - Export custom fields and doctypes
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["module", "=", "Consulting"]
        ]
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["module", "=", "Consulting"]
        ]
    },

    "Expertise Area",
    {
        "dt": "Workflow",
        "filters": [["name", "in", ["Consulting Task Workflow", "Deliverable Approval Workflow"]]]
    },
    {
        "dt": "Notification",
        "filters": [["name", "in", ["Deliverable Submitted", "Deliverable Approved", "Revision Required"]]]
    },
    "Client Contract",
    "Consultant Contract",
    "Deliverable"
]

# Document Events
doc_events = {
    "Project": {
        "validate": "backend.events.project_events.validate_project",
        "on_update": "backend.events.project_events.on_project_update"
    },
    "Task": {
        "validate": "backend.events.task_events.validate_task",
        "on_update": "backend.events.task_events.on_task_update",
        "before_save": "backend.events.task_events.on_task_before_save"
    },
    "Timesheet": {
        "validate": "backend.events.timesheet_events.on_timesheet_validate",
        "on_submit": "backend.events.timesheet_events.on_timesheet_submit",
        "on_cancel": "backend.events.timesheet_events.on_timesheet_cancel"
    },
    "Sales Invoice": {
        "on_submit": "backend.events.invoice_events.update_contract_invoiced",
        "on_cancel": "backend.events.invoice_events.revert_contract_invoiced"
    },
    "Deliverable": {
        "validate": "backend.events.deliverable_events.on_deliverable_validate",
        "on_update": "backend.events.deliverable_events.on_deliverable_update"
    }
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "backend.events.deliverable_events.send_overdue_alerts"
    ]
}
