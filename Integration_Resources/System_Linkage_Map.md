# System Linkage Map

This document establishes the binding between the User Interface (Frontend), the Application Logic (Backend), and the Database Hooks.

## 1. Project Management Module

### 1.1 Frontend: `public/js/project.js`
| Function (JS) | Backend Method (Python) | File Path | Purpose |
| :--- | :--- | :--- | :--- |
| `generate_project_invoice` | `generate_invoice_for_project` | `coms/consulting/billing/invoice_generator.py` | whitelist API to create sales invoices from unbilled timesheets. |
| `show_unbilled_summary` | `get_unbilled_summary` | `coms/consulting/billing/invoice_generator.py` | whitelist API to fetch total unbilled hours/amount for the dashboard indicator. |

### 1.2 Database Hooks: `Project` Doctype
| Event | Handler Function | File Path | Purpose |
| :--- | :--- | :--- | :--- |
| `validate` | `validate_project` | `coms/consulting/events/project_events.py` | Validates that the linked 'Client Contract' belongs to the correct Customer. Calculates Team Sizes (Internal/External). |
| `on_update` | `on_project_update` | `coms/consulting/events/project_events.py` | Syncs the Project to the 'Client Contract' project list. Updates Billing Status based on invoiced amount. |

---

## 2. Task Management Module

### 2.1 Frontend: `public/js/task.js`
| Function (JS) | Backend interaction | Purpose |
| :--- | :--- | :--- |
| `show_consultant_info` | `frappe.client.get_value('Employee')` | Fetches the standard `hourly_rate` directly from the Employee doctype. |
| `assigned_consultant` | `frappe.client.get_value('Consultant Contract')` | Auto-links the active contract to the task when a consultant is selected. |

### 2.2 Database Hooks: `Task` Doctype
| Event | Handler Function | File Path | Purpose |
| :--- | :--- | :--- | :--- |
| `validate` | `validate_task` | `coms/consulting/events/task_events.py` | Checks consultant availability overlap using `Project Consultant` allocation. |
| `on_update` | `on_task_update` | `coms/consulting/events/task_events.py` | Auto-adds the consultant to the Project Team if they aren't already there. Syncs to Frappe ToDo. |

---

## 3. Timesheet & Invoicing Module

### 3.1 Backend Logic
| Component | Function | File Path | Purpose |
| :--- | :--- | :--- | :--- |
| **Invoice Engine** | `generate_invoices_for_project` | `coms/consulting/billing/invoice_generator.py` | The core engine that aggregates timesheets, groups by customer, gets the rate from the Contract or Employee, and inserts `Sales Invoice` records. |
| **Timesheet Hook** | `on_timesheet_validate` | `coms/consulting/events/timesheet_events.py` | Ensures the correct billing rate is picked (Contract Rate vs Standard Rate) before the timesheet is submitted. |

---

## 4. Deliverables Module

### 4.1 Workflow Logic (`via hooks.py`)
| Component | Definition | File Path | Purpose |
| :--- | :--- | :--- | :--- |
| **Workflow** | `Deliverable Approval Workflow` | `Integration_Resources/structures/workflows/deliverable_workflow.json` | Defines the 8-stage approval process (Draft -> In Progress -> ... -> Final). |
| **Notifications** | `Deliverable Submitted` | (Via Setup Script) | Emails the approver when status changes to 'Submitted'. |
