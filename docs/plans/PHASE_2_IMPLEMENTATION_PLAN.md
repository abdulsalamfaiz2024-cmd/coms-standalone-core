# Phase 2: Core Forms & Data Implementation Plan
**Objective:** Upgrade the system's operational core to support professional Consulting Workflows (Dual Contracts, Dual Invoices, QA Deliverables).

## 1. Database Schema Migration (Backend)
**Task:** Execute SQL `ALTER TABLE` commands to inject new fields into the SQLite database.

| Table | New Columns to Add |
| :--- | :--- |
| **Consultancy_Assignments** (Client Contract) | `TotalContractValue` (REAL), `SignatoryName` (TEXT), `BillingContact` (TEXT), `PaymentTerms` (TEXT), `Objectives` (TEXT), `Scope_In` (TEXT), `Scope_Out` (TEXT), `Signed_Contract` (TEXT) |
| **AssignmentConsultantRoles** (Consultant Contract) | `ContractType` (TEXT), `PaymentTrigger` (TEXT), `ExpensePolicy` (TEXT), `NDA_Signed` (INT), `TerminationNotice` (TEXT), `Signed_Agreement` (TEXT) |
| **Client_Invoices** | `LineItems` (TEXT/JSON), `TaxID` (TEXT), `BankReference` (TEXT), `Terms` (TEXT), `PO_Number` (TEXT), `Invoice_File` (TEXT) |
| **Consultant_Invoices** | `LinkedTimesheets` (TEXT), `LinkedExpenses` (TEXT), `TaxAmount` (REAL), `Deductions` (REAL), `CleanTotal` (REAL), `Invoice_Upload` (TEXT) |
| **Deliverables** | `Version` (TEXT), `ReviewerID` (TEXT), `QualityMatrix` (TEXT), `RejectionReason` (TEXT), `Deliverable_File` (TEXT), `Internal_Comments` (TEXT) |

*   **Action Script:** Create and run `System_Core/backend/setup/migrations/001_schema_upgrade.py`.

## 2. Meta-definition Updates (Backend)
**Task:** update the JSON files in `System_Core/backend/doctype/` to match the new DB schema. This ensures the frontend form builder "sees" the new fields.
*   **Target Files:**
    *   `consultancy_assignments.json`
    *   `assignmentconsultantroles.json`
    *   `client_invoices.json`
    *   `consultant_invoices.json`
    *   `deliverables.json`

## 3. File Attachment System (Full Stack)
**Task:** Enable "Evidence-based" records (Upload Contract, Upload Invoice).

*   **Backend (`server.py`):**
    *   Ensure `/api/upload` can handle generic file types (PDF, DOCX) securely.
    *   Store files in `assets/uploads/YYYY/MM/`.
*   **Frontend (`enterprise_engine.js`):**
    *   Update `renderForm()` to detect `fieldtype: "Attach"`.
    *   Render a File Input + Upload Button.
    *   On upload success -> Write URL to the hidden text input.

## 4. Work Execution Sequence
1.  **[Backend]** Run Schema Migration Script (Safety First: Backup DB).
2.  **[Backend]** Update JSON Definition files.
3.  **[Frontend]** Implement `Attach` Field logic in JS.
4.  **[Verification]** Open "Client Contract" form -> See new fields -> Upload PDF -> Save -> Verify in SQL.

---
**Definition of Done:**
*   All 5 Doctypes have the new fields in SQL.
*   Frontend Forms display all new fields correctly.
*   User can upload a PDF and link it to a Contract.
*   No "Internal Server Errors" on saving complex JSON data (LineItems).
