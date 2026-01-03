
import frappe

def create_workspace():
    """Create the Consulting Workspace for sidebar navigation"""
    
    if frappe.db.exists("Workspace", "Consulting"):
        frappe.delete_doc("Workspace", "Consulting")
        print("Deleted existing Consulting workspace")
    
    workspace = frappe.new_doc("Workspace")
    workspace.name = "Consulting"
    workspace.label = "Consulting"
    workspace.title = "Consulting"  # Added title
    workspace.module = "Consulting"
    workspace.category = "Modules"
    workspace.icon = "briefcase"
    workspace.is_standard = 0
    
    # Add shortcuts
    shortcuts = [
        {"label": "Client Contract", "link_to": "Client Contract", "type": "DocType"},
        {"label": "Consultant Contract", "link_to": "Consultant Contract", "type": "DocType"},
        {"label": "Expertise Area", "link_to": "Expertise Area", "type": "DocType"},
        {"label": "Project", "link_to": "Project", "type": "DocType"},
        {"label": "Timesheet", "link_to": "Timesheet", "type": "DocType"},
    ]
    
    for s in shortcuts:
        workspace.append("shortcuts", {
            "label": s["label"],
            "link_to": s["link_to"],
            "type": s["type"]
        })
    
    # Add links section
    workspace.append("links", {
        "label": "Contracts",
        "type": "Card Break"
    })
    workspace.append("links", {
        "label": "Client Contract",
        "link_to": "Client Contract",
        "link_type": "DocType",
        "type": "Link"
    })
    workspace.append("links", {
        "label": "Consultant Contract",
        "link_to": "Consultant Contract",
        "link_type": "DocType",
        "type": "Link"
    })
    
    workspace.append("links", {
        "label": "Masters",
        "type": "Card Break"
    })
    workspace.append("links", {
        "label": "Expertise Area",
        "link_to": "Expertise Area",
        "link_type": "DocType",
        "type": "Link"
    })
    
    workspace.append("links", {
        "label": "Operations",
        "type": "Card Break"
    })
    workspace.append("links", {
        "label": "Project",
        "link_to": "Project",
        "link_type": "DocType",
        "type": "Link"
    })
    workspace.append("links", {
        "label": "Task",
        "link_to": "Task",
        "link_type": "DocType",
        "type": "Link"
    })
    workspace.append("links", {
        "label": "Timesheet",
        "link_to": "Timesheet",
        "link_type": "DocType",
        "type": "Link"
    })
    
    workspace.insert(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"✓ Consulting Workspace created successfully")

create_workspace()
