
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def customize_consultant():
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()

    print("Customizing Employee to Consultant...")

    # 1. Rename 'Employee' to 'Consultant' in UI
    # We use Property Setter to override the label
    make_property_setter("Employee", None, "label", "Consultant", "Data")
    # Also update the naming series label if possible or description
    
    # 2. Add Custom Fields for Qualifications and Specialization
    # Note: Email and Cell Number are standard fields in Employee: 'company_email', 'personal_email', 'cell_number'.
    # We will just ensure they are prominent or add specific ones if needed.
    
    specialization_options = (
        "Monitoring & Evaluation (M&E)\n"
        "Grant Writing & Management\n"
        "Capacity Building\n"
        "Strategic Planning\n"
        "Public Health\n"
        "Policy Analysis\n"
        "Humanitarian Aid\n"
        "Gender & Social Inclusion (GESI)\n"
        "Food Security & Livelihoods\n"
        "WASH (Water, Sanitation, Hygiene)\n"
        "Education & Youth\n"
        "Other"
    )

    create_custom_fields({
        "Employee": [
            {
                "label": "Consulting Specialization",
                "fieldname": "consulting_specialization",
                "fieldtype": "Select",
                "options": specialization_options,
                "insert_after": "designation", # Put it near Job Title
                "reqd": 0
            },
            {
                "label": "Highest Qualification",
                "fieldname": "highest_qualification",
                "fieldtype": "Data",
                "insert_after": "consulting_specialization",
                "description": "e.g., PhD in Economics, Masters in Public Health"
            },
            {
                "label": "Years of Experience",
                "fieldname": "years_of_experience",
                "fieldtype": "Float",
                "insert_after": "highest_qualification"
            }
        ]
    })
    
    # Ensure contact fields are in a good spot or just rely on standard. 
    # Standard Employee form has 'Contact Details' section.
    
    frappe.db.commit()
    print("✓ Employee renamed to 'Consultant' and fields added.")

customize_consultant()
