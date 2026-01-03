
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import os

def run_db_restore():
    # Initialize Frappe Environment
    if not frappe.db:
        frappe.init(site="frontend", sites_path=".")
        frappe.connect()
    
    print("Starting Persistent COMS Restoration...")

    # Helper to create Custom DocType
    def ensure_custom_doctype(dt_dict):
        if not frappe.db.exists("DocType", dt_dict["name"]):
            doc = frappe.get_doc(dt_dict)
            doc.custom = 1 
            doc.module = "Custom" # Store in global Custom module
            doc.insert()
            print(f"✓ DocType {dt_dict['name']} created")
        else:
            print(f"- DocType {dt_dict['name']} already exists")

    # 1. Expertise Area (Masters first)
    ensure_custom_doctype({
        "doctype": "DocType",
        "name": "Expertise Area",
        "autoname": "field:expertise_name",
        "fields": [
            {"fieldname": "expertise_name", "fieldtype": "Data", "label": "Expertise Name", "reqd": 1, "unique": 1, "in_list_view": 1},
            {"fieldname": "category", "fieldtype": "Select", "label": "Category", "options": "Technical\nManagement\nFinancial\nResearch\nIndustry-Specific\nSoft Skills", "in_list_view": 1},
            {"fieldname": "description", "fieldtype": "Small Text", "label": "Description"},
            {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": "1"}
        ],
        "permissions": [{"role": "System Manager", "read":1, "write":1, "create":1, "delete":1}]
    })

    # 2. Consultant Expertise (Child dependent on Expertise Area)
    ensure_custom_doctype({
        "doctype": "DocType",
        "name": "Consultant Expertise",
        "istable": 1,
        "fields": [
            {"fieldname": "expertise_area", "fieldtype": "Link", "label": "Expertise Area", "options": "Expertise Area", "reqd": 1, "in_list_view": 1},
            {"fieldname": "proficiency_level", "fieldtype": "Select", "label": "Proficiency Level", "options": "Beginner\nIntermediate\nAdvanced\nExpert", "in_list_view": 1},
            {"fieldname": "years_experience", "fieldtype": "Int", "label": "Years of Experience", "in_list_view": 1}
        ]
    })

    # 3. Contract Milestone (Child Table)
    ensure_custom_doctype({
        "doctype": "DocType",
        "name": "Contract Milestone",
        "istable": 1,
        "fields": [
            {"fieldname": "milestone_name", "fieldtype": "Data", "label": "Milestone Name", "reqd": 1, "in_list_view": 1},
            {"fieldname": "description", "fieldtype": "Small Text", "label": "Description"},
            {"fieldname": "due_date", "fieldtype": "Date", "label": "Due Date", "in_list_view": 1},
            {"fieldname": "amount", "fieldtype": "Currency", "label": "Amount", "reqd": 1, "in_list_view": 1},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Pending\nIn Progress\nCompleted\nInvoiced", "default": "Pending", "in_list_view": 1},
            {"fieldname": "completed_date", "fieldtype": "Date", "label": "Completed Date"}
        ]
    })

    # 4. Contract Project (Child Table)
    ensure_custom_doctype({
        "doctype": "DocType",
        "name": "Contract Project",
        "istable": 1,
        "fields": [
            {"fieldname": "project", "fieldtype": "Link", "label": "Project", "options": "Project", "reqd": 1, "in_list_view": 1},
            {"fieldname": "project_status", "fieldtype": "Data", "label": "Status", "read_only": 1, "fetch_from": "project.status", "in_list_view": 1},
            {"fieldname": "percent_complete", "fieldtype": "Percent", "label": "% Complete", "read_only": 1, "fetch_from": "project.percent_complete", "in_list_view": 1}
        ]
    })

    # 5. Project Consultant (Child Table) - Team
    ensure_custom_doctype({
        "doctype": "DocType",
        "name": "Project Consultant",
        "istable": 1,
        "fields": [
            {"fieldname": "consultant", "fieldtype": "Link", "label": "Consultant", "options": "Employee", "reqd": 1, "in_list_view": 1},
            {"fieldname": "role", "fieldtype": "Data", "label": "Role", "in_list_view": 1},
            {"fieldname": "hourly_rate", "fieldtype": "Currency", "label": "Hourly Rate", "in_list_view": 1},
            {"fieldname": "total_hours", "fieldtype": "Float", "label": "Total Allocated Hours", "in_list_view": 1},
            {"fieldname": "actual_hours", "fieldtype": "Float", "label": "Actual Hours", "read_only": 1, "in_list_view": 1}
        ]
    })

    # 6. Client Contract - Main DocType
    ensure_custom_doctype({
        "doctype": "DocType",
        "name": "Client Contract",
        "autoname": "naming_series:",
        "fields": [
            {"fieldname": "naming_series", "fieldtype": "Select", "label": "Series", "options": "CC-.YYYY.-.#####", "reqd": 1, "default": "CC-.YYYY.-.#####"},
            {"fieldname": "contract_title", "fieldtype": "Data", "label": "Contract Title", "reqd": 1, "in_list_view": 1},
            {"fieldname": "client", "fieldtype": "Link", "label": "Client", "options": "Customer", "reqd": 1, "in_list_view": 1},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nActive\nOn Hold\nCompleted\nCancelled", "default": "Draft", "in_list_view": 1},
            {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company", "reqd": 1, "default": frappe.defaults.get_user_default("Company")},
            {"fieldname": "contract_type", "fieldtype": "Select", "label": "Contract Type", "options": "Fixed Price\nRetainer\nTime & Materials\nMilestone-Based", "reqd": 1},
            {"fieldname": "start_date", "fieldtype": "Date", "label": "Start Date", "reqd": 1},
            {"fieldname": "end_date", "fieldtype": "Date", "label": "End Date"},
            {"fieldname": "currency", "fieldtype": "Link", "label": "Currency", "options": "Currency", "reqd": 1, "default": "USD"},
            {"fieldname": "contract_value", "fieldtype": "Currency", "label": "Contract Value", "options": "currency", "reqd": 1},
            {"fieldname": "milestones", "fieldtype": "Table", "label": "Milestones", "options": "Contract Milestone"},
            {"fieldname": "projects", "fieldtype": "Table", "label": "Projects", "options": "Contract Project", "read_only": 1}
        ],
        "permissions": [{"role": "System Manager", "read":1, "write":1, "create":1, "delete":1}]
    })

    # 7. Consultant Contract - Main DocType
    ensure_custom_doctype({
        "doctype": "DocType",
        "name": "Consultant Contract",
        "autoname": "naming_series:",
        "fields": [
            {"fieldname": "naming_series", "fieldtype": "Select", "label": "Series", "options": "CCON-.YYYY.-.#####", "reqd": 1, "default": "CCON-.YYYY.-.#####"},
            {"fieldname": "contract_title", "fieldtype": "Data", "label": "Contract Title", "reqd": 1, "in_list_view": 1},
            {"fieldname": "consultant", "fieldtype": "Link", "label": "Consultant", "options": "Employee", "reqd": 1, "in_list_view": 1},
            {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nActive\nOn Hold\nCompleted\nCancelled", "default": "Draft", "in_list_view": 1},
            {"fieldname": "start_date", "fieldtype": "Date", "label": "Start Date", "reqd": 1},
            {"fieldname": "end_date", "fieldtype": "Date", "label": "End Date"},
            {"fieldname": "rate_type", "fieldtype": "Select", "label": "Rate Type", "options": "Hourly\nDaily\nMonthly", "reqd": 1},
            {"fieldname": "rate_amount", "fieldtype": "Currency", "label": "Rate Amount", "reqd": 1}
        ],
        "permissions": [{"role": "System Manager", "read":1, "write":1, "create":1, "delete":1}]
    })

    # 8. Restore Custom Fields on Standard DocTypes
    custom_fields = {
        "Employee": [
            {"label": "Consultant Type", "fieldname": "consultant_type", "fieldtype": "Select", "options": "Internal\nExternal\nFreelance", "insert_after": "designation"},
            {"label": "Seniority Level", "fieldname": "seniority_level", "fieldtype": "Select", "options": "Junior\nMid-Level\nSenior\nExpert", "insert_after": "consultant_type"},
            {"label": "Hourly Rate", "fieldname": "hourly_rate", "fieldtype": "Currency", "insert_after": "seniority_level"},
            {"label": "Is Billable", "fieldname": "is_billable", "fieldtype": "Check", "default": "1", "insert_after": "hourly_rate"},
            {"label": "Expertise Areas", "fieldname": "expertise_areas", "fieldtype": "Table", "options": "Consultant Expertise", "insert_after": "is_billable"}
        ],
        "Customer": [
            {"label": "Organization Type", "fieldname": "organization_type", "fieldtype": "Select", "options": "Private\nPublic\nNGO\nGovernment\nInternational", "insert_after": "customer_type"},
            {"label": "Client Classification", "fieldname": "client_classification", "fieldtype": "Select", "options": "Strategic\nRegular\nNew\nOccasional", "insert_after": "organization_type"}
        ],
        "Project": [
            {"label": "Client Contract", "fieldname": "client_contract", "fieldtype": "Link", "options": "Client Contract", "insert_after": "customer"},
            {"label": "Consultant Team", "fieldname": "consultant_team", "fieldtype": "Table", "options": "Project Consultant", "insert_after": "client_contract"}
        ],
        "Task": [
            {"label": "Consultant Contract", "fieldname": "consultant_contract", "fieldtype": "Link", "options": "Consultant Contract", "insert_after": "project"}
        ],
        "Timesheet": [
            {"label": "Consultant Contract", "fieldname": "consultant_contract", "fieldtype": "Link", "options": "Consultant Contract", "insert_after": "employee", "read_only": 1},
            {"label": "Contract Rate Type", "fieldname": "contract_rate_type", "fieldtype": "Data", "insert_after": "consultant_contract", "read_only": 1}
        ],
        "Timesheet Detail": [
             {"label": "Contract Rate", "fieldname": "contract_rate", "fieldtype": "Currency", "insert_after": "billing_amount", "read_only": 1},
             {"label": "Consultant Rate", "fieldname": "consultant_rate", "fieldtype": "Currency", "insert_after": "contract_rate"},
             {"label": "Rate Source", "fieldname": "rate_source", "fieldtype": "Data", "insert_after": "consultant_rate", "read_only": 1},
             {"label": "Client Contract", "fieldname": "client_contract", "fieldtype": "Link", "options": "Client Contract", "insert_after": "project", "read_only": 1}
        ]
    }
    
    for dt, fields in custom_fields.items():
        create_custom_fields({dt: fields})
        print(f"✓ Custom fields for {dt} restored")
    
    frappe.db.commit()
    print("Database Schema Restoration Complete.")

run_db_restore()
