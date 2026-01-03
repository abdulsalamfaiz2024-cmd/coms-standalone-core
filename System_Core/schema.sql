CREATE TABLE IF NOT EXISTS "AssignmentConsultantRoles" (
    "id" TEXT PRIMARY KEY,
    "Index" TEXT,
    "Assignment" TEXT,
    "Consultant" TEXT,
    "Role_EN" TEXT,
    "Role_AR" TEXT,
    "Engagement_Level" TEXT,
    "DutyStation" TEXT,
    "StartDate_Assign" TEXT,
    "EndDate" TEXT,
    "Status" TEXT,
    "Planned_Days" TEXT,
    "Actual_Days" TEXT,
    "DailyRate_Contract" TEXT,
    "Rate_Currency" TEXT,
    "Fee_Planned" TEXT,
    "Fee_Actual" TEXT,
    "Timesheet_Required" TEXT,
    "Travel_Days" TEXT,
    "PerDiem_Applied" TEXT,
    "Performance_Rating" TEXT,
    "Feedback_Notes" TEXT,
    "Is_LeadRole" TEXT
);
CREATE TABLE IF NOT EXISTS "Clients" (
    "id" TEXT PRIMARY KEY,
    "Client_Name" TEXT,
    "ClientCode" TEXT,
    "ClientType" TEXT,
    "ContactEmail" TEXT,
    "Status" TEXT,
    "EndDate" TEXT
);
CREATE TABLE IF NOT EXISTS "Client_Contacts" (
    "id" TEXT PRIMARY KEY,
    "Client" TEXT,
    "ContactName" TEXT,
    "Position" TEXT,
    "Email" TEXT,
    "Phone" TEXT,
    "IsPrimary" TEXT,
    "Status" TEXT,
    "EndDate" TEXT
);
CREATE TABLE IF NOT EXISTS "Client_Invoices" (
    "id" TEXT PRIMARY KEY,
    "Assignment" TEXT,
    "InvoiceNumber" TEXT,
    "DateIssued" TEXT,
    "Amount" REAL,
    "Currency" TEXT,
    "Status" TEXT,
    "PaymentDate" TEXT
);
CREATE TABLE IF NOT EXISTS "Consultancy_Assignments" (
    "id" TEXT PRIMARY KEY,
    "Title" TEXT,
    "A_Code" TEXT,
    "Stage" TEXT,
    "Priority" TEXT,
    "Client" TEXT,
    "Funder" TEXT,
    "ContractRef" TEXT,
    "Status" TEXT,
    "LeadConsultant" TEXT,
    "Sector" TEXT,
    "ServiceLine" TEXT,
    "Country" TEXT,
    "Governorate" TEXT,
    "City" TEXT,
    "StartDate" TEXT,
    "EndDate" TEXT
);
CREATE TABLE IF NOT EXISTS "Consultants" (
    "id" TEXT PRIMARY KEY,
    "Consultants_name" TEXT,
    "Email" TEXT,
    "Phone" TEXT,
    "MainSector" TEXT,
    "CVLink" TEXT,
    "Rating" TEXT,
    "Nationality" TEXT,
    "Notes" TEXT,
    "JobTitle" TEXT,
    "Status" TEXT,
    "EndDate" TEXT
);
CREATE TABLE IF NOT EXISTS "Consultant_Availability" (
    "id" TEXT PRIMARY KEY,
    "Consultant" TEXT,
    "StartDate" TEXT,
    "EndDate" TEXT,
    "Status" TEXT
);
CREATE TABLE IF NOT EXISTS "Consultant_Education" (
    "id" TEXT PRIMARY KEY,
    "Consultant" TEXT,
    "Degree" TEXT,
    "FieldOfStudy" TEXT,
    "Institution" TEXT,
    "Year" TEXT
);
CREATE TABLE IF NOT EXISTS "Consultant_Invoices" (
    "id" TEXT PRIMARY KEY,
    "Consultant" TEXT,
    "Assignment" TEXT,
    "PeriodStart" TEXT,
    "PeriodEnd" TEXT,
    "TotalAmount" REAL,
    "ApprovalStatus" TEXT
);
CREATE TABLE IF NOT EXISTS "Consultant_Languages" (
    "id" TEXT PRIMARY KEY,
    "Consultant" TEXT,
    "Language" TEXT,
    "ReadingLevel" TEXT,
    "WritingLevel" TEXT,
    "SpeakingLevel" TEXT
);
CREATE TABLE IF NOT EXISTS "Consultant_Skills" (
    "id" TEXT PRIMARY KEY,
    "Consultant" TEXT,
    "Skill" TEXT,
    "Proficiency_1_5" TEXT,
    "YearsExperience" TEXT
);
CREATE TABLE IF NOT EXISTS "Countries" (
    "id" TEXT PRIMARY KEY,
    "country_name" TEXT,
    "ISOCode" TEXT,
    "Region" TEXT,
    "Active" TEXT
);
CREATE TABLE IF NOT EXISTS "Deliverables" (
    "id" TEXT PRIMARY KEY,
    "Assignment" TEXT,
    "Title" TEXT,
    "Description" TEXT,
    "DueDate" TEXT,
    "SubmissionDate" TEXT,
    "Status" TEXT,
    "PaymentPercentage" TEXT
);
CREATE TABLE IF NOT EXISTS "Expenses" (
    "id" TEXT PRIMARY KEY,
    "Assignment" TEXT,
    "Consultant" TEXT,
    "Category" TEXT,
    "Amount" REAL,
    "ReceiptImageURL" TEXT,
    "Status" TEXT
);
CREATE TABLE IF NOT EXISTS "Governorates" (
    "id" TEXT PRIMARY KEY,
    "Governorates" TEXT,
    "Country" TEXT,
    "Active" TEXT
);
CREATE TABLE IF NOT EXISTS "Interactions_Log" (
    "id" TEXT PRIMARY KEY,
    "Client" TEXT,
    "InteractionDate" TEXT,
    "Type" TEXT,
    "Notes" TEXT,
    "NextAction" TEXT
);
CREATE TABLE IF NOT EXISTS "Languages" (
    "id" TEXT PRIMARY KEY,
    "Title" TEXT,
    "ISOCode" TEXT
);
CREATE TABLE IF NOT EXISTS "Roles" (
    "id" TEXT PRIMARY KEY,
    "Job_title" TEXT
);
CREATE TABLE IF NOT EXISTS "Sectors" (
    "id" TEXT PRIMARY KEY,
    "Title" TEXT,
    "SectorCode" TEXT,
    "Description" TEXT,
    "Status" TEXT,
    "EndDate" TEXT
);
CREATE TABLE IF NOT EXISTS "ServiceLines" (
    "id" TEXT PRIMARY KEY,
    "ServiceLines" TEXT,
    "Category" TEXT,
    "Active" TEXT
);
CREATE TABLE IF NOT EXISTS "Skills" (
    "id" TEXT PRIMARY KEY,
    "Title" TEXT,
    "Category" TEXT,
    "Active" TEXT
);
CREATE TABLE IF NOT EXISTS "Stages" (
    "id" TEXT PRIMARY KEY,
    "Stages" TEXT,
    "SortOrder" TEXT,
    "Active" TEXT
);
CREATE TABLE IF NOT EXISTS "Statuses" (
    "id" TEXT PRIMARY KEY,
    "Statuses" TEXT,
    "SortOrder" TEXT,
    "Active" TEXT
);
CREATE TABLE IF NOT EXISTS "Tasks" (
    "id" TEXT PRIMARY KEY,
    "Assignment" TEXT,
    "Consultant" TEXT,
    "Title" TEXT,
    "DueDate" TEXT,
    "Contract_Ref" TEXT,
    "StartDate" TEXT,
    "EndDate" TEXT,
    "TaskDetails" TEXT,
    "Sessions" TEXT,
    "Hours" TEXT,
    "Days" TEXT,
    "Status" TEXT
);
CREATE TABLE IF NOT EXISTS "Users" (
    "id" TEXT PRIMARY KEY,
    "username" TEXT UNIQUE,
    "password_hash" TEXT,
    "full_name" TEXT,
    "role" TEXT,
    "email" TEXT
);
CREATE TABLE IF NOT EXISTS "Settings" (
    "key" TEXT PRIMARY KEY,
    "value" TEXT
);
CREATE TABLE IF NOT EXISTS "Files" (
    "id" TEXT PRIMARY KEY,
    "file_name" TEXT,
    "file_path" TEXT,
    "parent_doctype" TEXT,
    "parent_id" TEXT,
    "uploaded_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);