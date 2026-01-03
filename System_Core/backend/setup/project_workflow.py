
import frappe

def create_task_fields_and_workflow():
    # 1. Ensure Workflow States Exist (Already done by previous run, but harmless to repeat)
    states = [
        "Open", "Assigned", "In Progress", "Pending Review", 
        "Revision Required", "Completed", "Cancelled"
    ]
    for state in states:
        if not frappe.db.exists("Workflow State", state):
            doc = frappe.new_doc("Workflow State")
            doc.workflow_state_name = state
            doc.save()

    # 2. Ensure Workflow Actions Exist
    actions = [
        "Assign", "Start Work", "Submit for Review", "Approve", 
        "Request Revision", "Resume Work", "Cancel"
    ]
    for action in actions:
        if not frappe.db.exists("Workflow Action Master", action):
            doc = frappe.new_doc("Workflow Action Master")
            doc.workflow_action_name = action
            doc.save()
            print(f"Created Workflow Action: {action}")

    # 3. Create Workflow
    workflow_name = "Consulting Task Workflow"
    if not frappe.db.exists("Workflow", workflow_name):
        wf = frappe.new_doc("Workflow")
        wf.workflow_name = workflow_name
        wf.document_type = "Task"
        wf.is_active = 1
        wf.override_status = 0
        wf.send_email_alert = 1
        wf.workflow_state_field = "workflow_state"
        
        # States
        wf.states = []
        state_data = [
            {"state": "Open", "doc_status": 0, "allow_edit": "Projects Manager"},
            {"state": "Assigned", "doc_status": 0, "allow_edit": "Projects User"},
            {"state": "In Progress", "doc_status": 0, "allow_edit": "Projects User"},
            {"state": "Pending Review", "doc_status": 0, "allow_edit": "Projects Manager"},
            {"state": "Revision Required", "doc_status": 0, "allow_edit": "Projects User"},
            {"state": "Completed", "doc_status": 0, "allow_edit": "Projects Manager"},
            {"state": "Cancelled", "doc_status": 0, "allow_edit": "Projects Manager"},
        ]
        
        for s in state_data:
            wf.append("states", {
                "state": s["state"],
                "doc_status": s["doc_status"],
                "allow_edit": s["allow_edit"]
            })
            
        # Transitions
        wf.transitions = []
        trans_data = [
            {"state": "Open", "action": "Assign", "next_state": "Assigned", "allowed": "Projects Manager"},
            {"state": "Assigned", "action": "Start Work", "next_state": "In Progress", "allowed": "Projects User", "allow_self_approval": 1},
            {"state": "In Progress", "action": "Submit for Review", "next_state": "Pending Review", "allowed": "Projects User", "allow_self_approval": 1},
            {"state": "Pending Review", "action": "Approve", "next_state": "Completed", "allowed": "Projects Manager"},
            {"state": "Pending Review", "action": "Request Revision", "next_state": "Revision Required", "allowed": "Projects Manager"},
            {"state": "Revision Required", "action": "Resume Work", "next_state": "In Progress", "allowed": "Projects User", "allow_self_approval": 1},
            {"state": "In Progress", "action": "Cancel", "next_state": "Cancelled", "allowed": "Projects Manager"},
            {"state": "Open", "action": "Cancel", "next_state": "Cancelled", "allowed": "Projects Manager"},
            {"state": "Assigned", "action": "Cancel", "next_state": "Cancelled", "allowed": "Projects Manager"}
        ]
        
        for t in trans_data:
            wf.append("transitions", {
                "state": t["state"],
                "action": t["action"],
                "next_state": t["next_state"],
                "allowed": t["allowed"],
                "allow_self_approval": t.get("allow_self_approval", 0)
            })
            
        wf.save()
        print(f"Created Workflow: {workflow_name}")
    else:
        print(f"Workflow {workflow_name} already exists")

    frappe.db.commit()

create_task_fields_and_workflow()
