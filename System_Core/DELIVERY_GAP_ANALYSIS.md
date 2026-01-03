# Delivery Gap Analysis: Consultancy OS

## 🚨 Critical Launch Blockers (Must-Have)

### 1. Authentication & Security (The "Open Door" Problem)
*   **Current State:** The system has **Zero Security**. No login screen, no session tokens, no password protection.
*   **Risk:** Anyone with network access can read contracts, salary data, and delete/modify client lists.
*   **Requirement:** Implement a Login Screen, JWT/Session management, and a `Users` table with hashed passwords.

### 2. Record Deletion & Archiving
*   **Current State:** Users can Create and Edit, but **cannot Delete** mistakes.
*   **Risk:** The database will fill up with test data, duplicates, and errors that cannot be removed, frustrating users.
*   **Requirement:** Add a "Delete/Archive" button to the form and a corresponding secure API endpoint (`/api/delete`).

### 3. Business Logic validation
*   **Current State:** The server blindly accepts whatever the frontend sends.
*   **Risk:** A user could enter an "End Date" that is *before* the "Start Date", or a negative numeric value for "Hours".
*   **Requirement:** Server-side validation checks in `db_engine.py`.

---

## ⚠️ Operational Essentials (Should-Have)

### 4. Audit Logging (Traceability)
*   **Current State:** No record of who changed what context.
*   **Risk:** If a contract value is changed, there is no way to know *who* did it or *when*.
*   **Requirement:** An `Activity Log` or `Audit Trail` feature visible on the record.

### 5. Data Export (Reporting)
*   **Current State:** Data is locked in the dashboard.
*   **Risk:** Managers cannot export lists to Excel/CSV for external reporting or meetings.
*   **Requirement:** A simple "Export to CSV" button on the List views.

### 6. Document Attachments
*   **Current State:** Text-only data.
*   **Risk:** Consultants cannot upload actual PDF Contracts, CVs, or Scanned Invoices.
*   **Requirement:** File upload capability and storage.

---

## 🛠 User Experience Polish (Nice-to-Have)

### 7. Global Search Improvement
*   **Current State:** Basic text matching.
*   **Requirement:** Advanced filters (e.g., "Show me all Active Projects in Egypt > $50k").

### 8. User Roles & Permissions
*   **Current State:** (If Auth is added) Everyone is Admin.
*   **Requirement:** Separate "Consultants" (can only see their tasks) vs "Partners" (can see financial data).
