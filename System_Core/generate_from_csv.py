
import os
import json
import csv
import re
import sqlite3

BASE_DIR = "d:/Custom_System_Copy/DB_table"
OUTPUT_DIR = "d:/Custom_System_Copy/System_Core/backend/doctype"
DB_FILE = "d:/Custom_System_Copy/System_Core/system.db"

TITLE_MAP = {
    'Clients': 'Client_Name',
    'Countries': 'country_name',
    'Governorates': 'Governorates',
    'Sectors': 'Title',
    'ServiceLines': 'ServiceLines',
    'Stages': 'Stages',
    'Statuses': 'Statuses',
    'Roles': 'Job_title',
    'Consultancy_Assignments': 'A_Title',
    'Consultants': 'Consultants_name',
    'Skills': 'Title',
    'Languages': 'Title',
    'Deliverables': 'Title',
    'Tasks': 'Title',
    'Client_Invoices': 'InvoiceNumber',
    'Client_Contacts': 'ContactName'
}

FILES_TO_PROCESS = [
    "Clients.csv", "Countries.csv", "Governorates.csv", "Sectors.csv", 
    "ServiceLines.csv", "Stages.csv", "Statuses.csv", "Role.csv",
    "Consultancy_Assignments.csv", "Consultants.csv", "Assignment–Consultant Roles.csv",
    "Skills.csv", "Languages.csv", "Consultant_Skills.csv", "Consultant_Languages.csv",
    "Consultant_Education.csv", "Consultant_Availability.csv",
    "Deliverables.csv", "Tasks.csv",
    "Client_Invoices.csv", "Consultant_Invoices.csv", "Expenses.csv",
    "Client_Contacts.csv", "Interactions_Log.csv"
]

def get_doctype_name(fname):
    name = fname.replace('.csv', '').replace('–', '-').replace('Assignment-Consultant Roles', 'AssignmentConsultantRoles')
    if name == "Role": name = "Roles"
    return name

lookup_map = {
    'Client': 'Clients', 'Client_Name': 'Clients',
    'Country': 'Countries',
    'Gov': 'Governorates', 'Governorate': 'Governorates',
    'Sector': 'Sectors', 'MainSector': 'Sectors',
    'ServiceLine': 'ServiceLines', 'Service_Line': 'ServiceLines',
    'Stage': 'Stages',
    'Status': 'Statuses',
    'Role': 'Roles', 'Role_EN': 'Roles',
    'Assignment': 'Consultancy_Assignments',
    'Consultant': 'Consultants',
    'Skill': 'Skills',
    'Language': 'Languages'
}

def parse_csv(fname):
    filepath = os.path.join(BASE_DIR, fname)
    if not os.path.exists(filepath): return None, None, []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    if not lines: return None, None, []
    
    # Process Line 1: Schema (ignore for now, we'll use headers)
    # Process Line 2: Headers
    header_line = lines[1].strip()
    headers = next(csv.reader([header_line]))
    
    # Process Line 3+: Data
    data = []
    if len(lines) > 2:
        reader = csv.reader(lines[2:])
        for row in reader:
            if row:
                row_dict = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
                data.append(row_dict)
    
    return headers, data

def create_doctype_json(dt_name, headers):
    fields = []
    
    for h in headers:
        if h.lower() == 'id': continue
        
        field = {
            "fieldname": h,
            "label": h.replace('_', ' ').title(),
            "fieldtype": "Data"
        }
        
        # Assign Link types
        if h in lookup_map:
            field["fieldtype"] = "Link"
            field["options"] = lookup_map[h]
        
        # Guess other types
        elif 'date' in h.lower():
            field["fieldtype"] = "Date"
        elif 'usd' in h.lower() or 'value' in h.lower() or 'amount' in h.lower():
            field["fieldtype"] = "Currency"
        elif h == 'Notes' or h == 'Lessons_Learned':
            field["fieldtype"] = "Long Text"
            
        fields.append(field)
    
    dt_dir = os.path.join(OUTPUT_DIR, dt_name.lower())
    os.makedirs(dt_dir, exist_ok=True)
    
    dt_json = {
        "name": dt_name,
        "doctype": "DocType",
        "fields": fields
    }
    
    with open(os.path.join(dt_dir, f"{dt_name.lower()}.json"), 'w') as f:
        json.dump(dt_json, f, indent=4)
    
    print(f"Created Doctype: {dt_name}")

def import_to_db(dt_name, data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    for row in data:
        name = row.get('ID') or row.get(TITLE_MAP.get(dt_name, 'Title')) or f"new-{dt_name}-{row.get('Title', 'item')}"
        row['doctype'] = dt_name
        row['name'] = name
        
        json_data = json.dumps(row)
        cursor.execute("INSERT OR REPLACE INTO docs (doctype, name, json) VALUES (?, ?, ?)", 
                       (dt_name, str(name), json_data))
    
    conn.commit()
    conn.close()
    print(f"Imported {len(data)} items for {dt_name}")

def main():
    for fname in FILES_TO_PROCESS:
        dt_name = get_doctype_name(fname)
        headers, data = parse_csv(fname)
        if headers:
            create_doctype_json(dt_name, headers)
            import_to_db(dt_name, data)
    
    print("Done generating doctypes and importing data.")

if __name__ == "__main__":
    main()
