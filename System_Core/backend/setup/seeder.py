
"""
Database Seeder
Populates the standalone system with initial demo data.
"""

from frappe import db, new_doc, today

def seed():
    print("Seeding Database...")
    
    # 1. Create Consultant (Employee)
    if not db.get_value("Employee", {"name": "EMP-001"}):
        e = new_doc("Employee")
        e.name = "EMP-001"
        e.employee_name = "Jamie Consultant"
        e.user_id = "Administrator"
        e.designation = "Senior Consultant"
        e.status = "Active"
        e.hourly_rate = 150.0
        e.save()
        print(" - Created Employee: Jamie Consultant")

    # 2. Create Project
    if not db.get_value("Project", {"name": "PROJ-001"}):
        p = new_doc("Project")
        p.name = "PROJ-001"
        p.project_name = "Digital Transformation Strategy"
        p.status = "Open"
        p.percent_complete = 25
        p.expected_end_date = "2026-06-30"
        p.project_type = "Strategy"
        p.save()
        
        # Link Consultant
        # Since we don't have child table logic fully Shimmed in 'append', 
        # we manually create the child doc linkage if needed, 
        # but for this POC the API uses a JOIN on 'tabProject Consultant'.
        # Our shim doesn't support complex SQL JOINs on the JSON blobs easily.
        # So we will update the get_my_dashboard API to look at the link directly 
        # or we update the Shim to support a "Link Table" concept (too complex).
        
        # SIMPLIFICATION:
        # We will create a "Project Consultant" DocType entry directly
        # that mimics the SQL table row.
        pc = new_doc("Project Consultant")
        pc.parent = "PROJ-001" # Link to project
        pc.parenttype = "Project"
        pc.parentfield = "consultant_team"
        pc.consultant = "EMP-001"
        pc.role = "Lead"
        pc.allocation_percentage = 100
        pc.save()
        
        print(" - Created Project: PROJ-001")

    # 3. Create Task
    if not db.get_value("Task", {"name": "TASK-001"}):
        t = new_doc("Task")
        t.name = "TASK-001"
        t.subject = "Initial Audit Report"
        t.project = "PROJ-001"
        t.status = "Open"
        t.assigned_consultant = "EMP-001"
        t.exp_end_date = today()
        t.priority = "High"
        t.save()
        print(" - Created Task: TASK-001")

if __name__ == "__main__":
    seed()
