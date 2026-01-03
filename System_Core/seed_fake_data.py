
import sqlite3
import uuid
import random
from datetime import datetime, timedelta

DB_PATH = r'd:\Custom_System_Copy\System_Core\consultancy.db'

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tables to seed
    tables = [
        "Stages", "Statuses", "Countries", "Governorates", "ServiceLines", 
        "Sectors", "Clients", "Consultants", "Consultancy_Assignments", 
        "Client_Contacts", "AssignmentConsultantRoles"
    ]
    
    # Clear existing data
    for t in tables:
        try:
            cursor.execute(f"DELETE FROM {t}")
        except:
            pass

    # 1. Stages
    stages = ["Proposal", "Evaluation", "Active", "Completed", "Cancelled"]
    stage_ids = []
    for s in stages:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO Stages (id, Stages) VALUES (?, ?)", (uid, s))
        stage_ids.append(uid)

    # 2. Statuses
    statuses = ["Critical", "Normal", "Delayed"]
    status_ids = []
    for s in statuses:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO Statuses (id, Statuses) VALUES (?, ?)", (uid, s))
        status_ids.append(uid)

    # 3. Countries
    countries = ["Jordan", "Lebanon", "Iraq", "Egypt", "Syria"]
    country_ids = []
    for c in countries:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO Countries (id, country_name) VALUES (?, ?)", (uid, c))
        country_ids.append(uid)

    # 4. Governorates
    govs = [
        ("Amman", country_ids[0]), ("Zarqa", country_ids[0]),
        ("Beirut", country_ids[1]), ("Sidon", country_ids[1]),
        ("Baghdad", country_ids[2]), ("Basra", country_ids[2]),
        ("Cairo", country_ids[3]), ("Alexandria", country_ids[3]),
        ("Damascus", country_ids[4]), ("Aleppo", country_ids[4])
    ]
    gov_ids = []
    for g, cid in govs:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO Governorates (id, Governorates, Country) VALUES (?, ?, ?)", (uid, g, cid))
        gov_ids.append(uid)

    # 5. ServiceLines
    services = ["Capacity Building", "Monitoring & Evaluation", "Strategic Planning", "Field Research", "Humanitarian Audit"]
    service_ids = []
    for s in services:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO ServiceLines (id, ServiceLines) VALUES (?, ?)", (uid, s))
        service_ids.append(uid)

    # 6. Sectors
    sectors = [
        ("Human Rights", "HR-01"), ("Environmental Protection", "ENV-02"), 
        ("Education & Literacy", "EDU-03"), ("Health & Nutrition", "HLT-04"), 
        ("Gender Equality", "GEN-05"), ("Economic Development", "ECON-06")
    ]
    sector_ids = []
    for s, code in sectors:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO Sectors (id, Title, SectorCode, Description, Status) VALUES (?, ?, ?, ?, ?)", 
                       (uid, s, code, f"Focused on {s} initiatives", "Active"))
        sector_ids.append(uid)

    # 7. Clients
    clients_data = [
        ("UNICEF", "UN-CH-01", "UN Agency", "contact@unicef.org"),
        ("UNDP", "UN-DV-02", "UN Agency", "info@undp.org"),
        ("Save the Children", "NGO-SC-03", "International NGO", "support@savethechildren.org"),
        ("Oxfam International", "NGO-OX-04", "International NGO", "contact@oxfam.org"),
        ("USAID", "GOV-US-05", "Governmental", "mission@usaid.gov")
    ]
    client_ids = []
    for name, code, ctype, email in clients_data:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO Clients (id, Client_Name, ClientCode, ClientType, ContactEmail, Status) VALUES (?, ?, ?, ?, ?, ?)",
                       (uid, name, code, ctype, email, "Active"))
        client_ids.append(uid)

    # 7.1 Client Contacts
    for cid in client_ids:
        for i in range(2):
            uid = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO Client_Contacts (id, Client, ContactName, Position, Email, Phone, IsPrimary, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (uid, cid, f"Contact Person {i+1}", "Program Manager", f"contact{i+1}@client.org", "+962 7XXX XXXX", "Yes" if i==0 else "No", "Active"))

    # 8. Consultants
    consultants_data = [
        ("Dr. Sarah Jenkins", "sarah.j@experts.com", "Senior M&E Specialist"),
        ("Ahmed Al-Masri", "ahmed.m@consultancy.com", "Civil Society Expert"),
        ("Maria Rossi", "m.rossi@field.org", "Humanitarian Auditor"),
        ("Jean Dupont", "j.dupont@strategy.com", "Strategic Advisor"),
        ("Laila Khalidi", "l.khalidi@rights.org", "Human Rights Legalist")
    ]
    consultant_ids = []
    for name, email, job in consultants_data:
        uid = str(uuid.uuid4())
        cursor.execute("INSERT INTO Consultants (id, Consultants_name, Email, JobTitle, MainSector, Status) VALUES (?, ?, ?, ?, ?, ?)",
                       (uid, name, email, job, random.choice(sector_ids), "Active"))
        consultant_ids.append(uid)

    # 9. Consultancy Assignments
    project_names = [
        "Regional Education Assessment", "Water Sanitation Audit", 
        "Gender Sensitization Training", "Post-Conflict Reconstruction Survey",
        "Refugee Integration Strategy", "Climate Resilience Planning"
    ]
    
    assignment_ids = []
    for i in range(6):
        uid = str(uuid.uuid4())
        assignment_ids.append(uid)
        start_date = datetime.now() - timedelta(days=random.randint(0, 100))
        end_date = start_date + timedelta(days=random.randint(60, 365))
        
        cursor.execute("""
            INSERT INTO Consultancy_Assignments 
            (id, Title, A_Code, Stage, Priority, Client, Funder, ContractRef, Status, LeadConsultant, Sector, ServiceLine, Country, Governorate, City, StartDate, EndDate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uid, project_names[i], f"PRJ-{2024}-{i+1:03d}", 
            random.choice(stage_ids), random.choice(["High", "Medium", "Low"]),
            random.choice(client_ids), "Multiple Funders" if i % 2 == 0 else "Single Institutional",
            f"REF-{random.randint(1000, 9999)}", "Active",
            random.choice(consultant_ids), random.choice(sector_ids), random.choice(service_ids),
            random.choice(country_ids), random.choice(gov_ids), "District " + str(i+1),
            start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
        ))

    # 9.1 Assignment Consultant Roles (Consultant Contracts)
    for aid in assignment_ids:
        # Assign 2-3 consultants per project
        chosen_consultants = random.sample(consultant_ids, k=random.randint(2, 3))
        for con_id in chosen_consultants:
            uid = str(uuid.uuid4())
            start_date = datetime.now()
            end_date = start_date + timedelta(days=90)
            cursor.execute("""
                INSERT INTO AssignmentConsultantRoles (id, Assignment, Consultant, Engagement_Level, StartDate_Assign, EndDate, Status, DailyRate_Contract)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (uid, aid, con_id, "Full Time", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "Active", "500 USD"))

    # 10. Tasks (New Detailed Structure)
    for aid in assignment_ids:
        # Create 3-5 tasks per assignment
        for i in range(random.randint(3, 5)):
            uid = str(uuid.uuid4())
            start_date = datetime.now() + timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(1, 5))
            
            cursor.execute("""
                INSERT INTO Tasks (id, Assignment, Consultant, Title, DueDate, Contract_Ref, StartDate, EndDate, TaskDetails, Sessions, Hours, Days, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uid, aid, random.choice(consultant_ids), f"Task {i+1}: Implementation Phase", 
                end_date.strftime('%Y-%m-%d'), f"CTR-{random.randint(100,999)}",
                start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                "Detailed description of the task activities and deliverables.",
                str(random.randint(1, 10)), str(random.randint(5, 40)), str(random.randint(1, 5)),
                "Active"
            ))

                "Active"
            ))

    # 11. Users (Admin)
    print("Seeding Users...")
    cursor.execute("DELETE FROM Users WHERE username='admin'") # Prevent duplicates
    cursor.execute("""
        INSERT INTO Users (id, username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()), "admin", hash_password("admin123"), "System Administrator", "Administrator"))

    conn.commit()
    conn.close()
    print("Database seeded successfully with a rich dataset of relationships.")

if __name__ == "__main__":
    seed()
