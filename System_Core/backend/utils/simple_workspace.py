
import frappe

def create_simple_workspace():
    """Create a simple Consulting Workspace"""
    
    # Delete any existing
    for ws in frappe.get_all("Workspace", filters={"module": "Consulting"}):
        frappe.delete_doc("Workspace", ws.name, force=True)
    if frappe.db.exists("Workspace", "Consulting"):
        frappe.delete_doc("Workspace", "Consulting", force=True)
    frappe.db.commit()
    
    workspace = frappe.new_doc("Workspace")
    workspace.name = "Consulting"
    workspace.label = "Consulting"
    workspace.title = "Consulting"
    workspace.module = "Consulting"
    workspace.category = "Modules"
    workspace.icon = "users"
    workspace.public = 1
    
    # Simple shortcuts
    for item in [
        ("Employee", "New Consultant"),
        ("Customer", "New Client"),
        ("Client Contract", "New Contract"),
        ("Project", "New Project"),
    ]:
        workspace.append("shortcuts", {
            "label": item[1],
            "link_to": item[0],
            "type": "DocType"
        })
    
    # Links
    for card in ["Masters", "Contracts", "Execution"]:
        workspace.append("links", {"label": card, "type": "Card Break"})
        
        if card == "Masters":
            for dt in ["Employee", "Customer", "Expertise Area"]:
                workspace.append("links", {"label": dt, "link_to": dt, "link_type": "DocType", "type": "Link"})
        elif card == "Contracts":
            for dt in ["Client Contract", "Consultant Contract"]:
                workspace.append("links", {"label": dt, "link_to": dt, "link_type": "DocType", "type": "Link"})
        else:
            for dt in ["Project", "Task", "Timesheet"]:
                workspace.append("links", {"label": dt, "link_to": dt, "link_type": "DocType", "type": "Link"})
    
    workspace.flags.ignore_links = True
    workspace.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Workspace created")

create_simple_workspace()
