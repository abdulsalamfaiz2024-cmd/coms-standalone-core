
import frappe

def create_project_templates():
    
    # Ensure Project Type "Consulting" exists
    if not frappe.db.exists("Project Type", "Consulting"):
        doc = frappe.new_doc("Project Type")
        doc.project_type = "Consulting"
        doc.save()
        print("Created Project Type: Consulting")
    
    if not frappe.db.exists("Project Template", "Standard Consulting Engagement"):
        # Create template with tasks initially populated
        template = frappe.new_doc("Project Template")
        template.name = "Standard Consulting Engagement"
        template.project_type = "Consulting" 
        
        # Add tasks
        tasks = [
            {"subject": "Inception Meeting", "weight": 5, "duration": 2},
            {"subject": "Data Collection", "weight": 20, "duration": 10},
            {"subject": "Data Analysis", "weight": 25, "duration": 10},
            {"subject": "Draft Report", "weight": 25, "duration": 8},
            {"subject": "Client Review", "weight": 10, "duration": 5},
            {"subject": "Final Report", "weight": 10, "duration": 3},
            {"subject": "Project Closeout", "weight": 5, "duration": 2}
        ]

        for task_data in tasks:
            task = frappe.new_doc("Task")
            task.subject = task_data["subject"]
            task.is_template = 1
            task.save()
            
            template.append("tasks", {
                "subject": task_data["subject"],
                "task": task.name, 
                "duration": task_data["duration"],
                "task_weight": task_data["weight"],
                "start": 0 
            })
            
        template.save()
        print(f"Created template: {template.name}")
    else:
        print("Template 'Standard Consulting Engagement' already exists")

    if not frappe.db.exists("Project Template", "Research Study"):
        # Create template
        template = frappe.new_doc("Project Template")
        template.name = "Research Study"
        template.project_type = "Consulting" 
        
        tasks = [
            {"subject": "Literature Review", "weight": 15, "duration": 10},
            {"subject": "Methodology Design", "weight": 15, "duration": 5},
            {"subject": "Data Collection", "weight": 25, "duration": 15},
            {"subject": "Data Analysis", "weight": 20, "duration": 10},
            {"subject": "Report Drafting", "weight": 15, "duration": 8},
            {"subject": "Peer Review", "weight": 5, "duration": 3},
            {"subject": "Final Submission", "weight": 5, "duration": 2}
        ]
        
        for task_data in tasks:
            task = frappe.new_doc("Task")
            task.subject = task_data["subject"]
            task.is_template = 1
            task.save()

            template.append("tasks", {
                "subject": task_data["subject"],
                "task": task.name,
                "duration": task_data["duration"],
                "task_weight": task_data["weight"],
                "start": 0 
            })
            
        template.save()
        print(f"Created template: {template.name}")
    else:
        print("Template 'Research Study' already exists")

    frappe.db.commit()


create_project_templates()
