
import frappe

def create_full_workspace():
    """Create a complete Consulting Workspace with proper layout"""
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()
    
    # Delete existing
    if frappe.db.exists("Workspace", "Consulting"):
        frappe.delete_doc("Workspace", "Consulting", force=True)
        frappe.db.commit()
        print("Deleted old workspace")
    
    workspace = frappe.new_doc("Workspace")
    workspace.name = "Consulting"
    workspace.label = "Consulting"
    workspace.title = "Consulting Operations"
    workspace.module = "Consulting"
    workspace.category = "Modules"
    workspace.icon = "users"
    workspace.is_standard = 0
    workspace.public = 1
    
    # SHORTCUTS - Quick action buttons at the top
    workspace.append("shortcuts", {
        "label": "New Consultant",
        "link_to": "Employee",
        "type": "DocType",
        "doc_view": "New"
    })
    workspace.append("shortcuts", {
        "label": "New Client",
        "link_to": "Customer",
        "type": "DocType",
        "doc_view": "New"
    })
    workspace.append("shortcuts", {
        "label": "New Client Contract",
        "link_to": "Client Contract",
        "type": "DocType",
        "doc_view": "New"
    })
    workspace.append("shortcuts", {
        "label": "New Project",
        "link_to": "Project",
        "type": "DocType",
        "doc_view": "New"
    })
    
    # LINKS Section - Master Data
    workspace.append("links", {
        "label": "Master Data",
        "type": "Card Break"
    })
    workspace.append("links", {
        "label": "Consultants (Employees)",
        "link_to": "Employee",
        "link_type": "DocType",
        "type": "Link"
    })
    workspace.append("links", {
        "label": "Clients (Customers)",
        "link_to": "Customer",
        "link_type": "DocType",
        "type": "Link"
    })
    workspace.append("links", {
        "label": "Expertise Areas",
        "link_to": "Expertise Area",
        "link_type": "DocType",
        "type": "Link"
    })
    
    # LINKS Section - Contracts
    workspace.append("links", {
        "label": "Contracts",
        "type": "Card Break"
    })
    workspace.append("links", {
        "label": "Client Contracts",
        "link_to": "Client Contract",
        "link_type": "DocType",
        "type": "Link"
    })
    workspace.append("links", {
        "label": "Consultant Contracts",
        "link_to": "Consultant Contract",
        "link_type": "DocType",
        "type": "Link"
    })
    
    # LINKS Section - Project Execution
    workspace.append("links", {
        "label": "Project Execution",
        "type": "Card Break"
    })
    workspace.append("links", {
        "label": "Projects",
        "link_to": "Project",
        "link_type": "DocType",
        "type": "Link"
    })
    workspace.append("links", {
        "label": "Tasks",
        "link_to": "Task",
        "link_type": "DocType",
        "type": "Link"
    })
    workspace.append("links", {
        "label": "Timesheets",
        "link_to": "Timesheet",
        "link_type": "DocType",
        "type": "Link"
    })
    
    workspace.flags.ignore_links = True
    workspace.insert(ignore_permissions=True)
    frappe.db.commit()
    
    print("✓ Consulting Workspace created with full layout")

create_full_workspace()
