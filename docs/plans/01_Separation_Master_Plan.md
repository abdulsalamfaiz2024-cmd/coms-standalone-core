# COMS System Separation Master Plan

## 1. Executive Summary
This document outlines the strategic plan to decouple the **Consultant Operations & Management System (COMS)** from the core ERPNext interface. The goal is to create a dedicated, focused environment for consultants that remains fully integrated with ERPNext's powerful backend (HR, Accounting, CRM) while providing a streamlined, role-specific user experience.

**Objective:** Transform COMS from an "internal module" into a "Specialized Consultant System" that interacts with ERPNext as its engine.

---

## 2. Architectural Vision

### Current State (Monolithic)
*   **Interface:** Consultants log into the standard ERPNext Desk.
*   **Navigation:** Mixed with standard ERPNext modules (Buying, Stock, Assets).
*   **Logic:** Tightly coupled event handlers in `hooks.py`.

### Future State (Decoupled & Integrated)
The system will be split into two logical layers:

#### A. The Core Engine (ERPNext + COMS Backend)
*   **Role:** Data System of Record & Processing Engine.
*   **Responsibility:**
    *   **HR:** Payroll, Leave, Employee Master.
    *   **Accounting:** General Ledger, Banking, Financial Statements.
    *   **Admin:** System Configuration, User Management.
*   **Access:** Admins, HR Managers, Finance Team only.

#### B. The Consultant Portal (The "Separated System")
*   **Role:** The Operational Interface for Consultants.
*   **Technology:** Frappe Portal Pages or a Single Page Application (SPA) utilizing the detailed JSON doctypes we created.
*   **Responsibility:**
    *   **Client Acquisition:** Leads, Proposals, Contract Generation.
    *   **Execution:** Task Boards, Timesheets, Deliverable Uploads.
    *   **Billing:** Invoice Request/Generation (Consultant view).
    *   **Performance:** Feedback, Skill Profile updates.
*   **Access:** Consultants, Project Managers.

---

## 3. Functional Separation Plan

### 3.1 HR & Profile Management
*   **Separation:** Consultants no longer access the "Employee" document directly.
*   **New Workflow:**
    *   Consultants manage a **"Consultant Profile"** (Self-Service).
    *   Updates (Skills, Bio) require approval to sync to the `Employee` master.
    *   Leave/Expense claims handled via simplified Portal forms, syncing to ERPNext HR.

### 3.2 Client Acquisition & CRM
*   **Separation:** Restrict full "Customer" and "Opportunity" access.
*   **New Workflow:**
    *   Consultants use a **"Client Onboarding Wizard"** to register prospects.
    *   **"Contract Builder"**: A specialized interface to draft `Client Contract` documents without seeing the full accounting fields.

### 3.3 Project & Task Management
*   **Separation:** Hide the complex ERPNext "Project" form.
*   **New Workflow:**
    *   **"Mission Control Center"**: A dashboard showing active Tasks and Deliverables.
    *   **Kanban/List View**: Simplified task management focused on status and time logging.
    *   **Deliverable Hub**: Drag-and-drop interface for `Deliverable` submission and revision history.

### 3.4 Accounting & Invoicing
*   **Separation:** Consultants never touch `Sales Invoice` or `Payment Entry` meant for Accountants.
*   **New Workflow:**
    *   **"Smart Billing"**: Consultants trigger "Invoice Requests" based on milestones or timesheets.
    *   The System (Backend) generates the `Sales Invoice` automatically.
    *   Consultants view **"Financial Status"** (Invoiced vs. Paid) for their projects without accessing the General Ledger.

---

## 4. Integration Strategy

Despite the separation, the system remains strictly integrated via:
1.  **Shared Database (MariaDB):** Both the Core and Portal read/write to the same data source, ensuring real-time accuracy.
2.  **API Layer:** The Consultant System uses restricted Server Scripts/API calls to fetch data, ensuring they only see what they own (Row-Level Security).
3.  **Event Webhooks:** Changes in ERPNext (e.g., Invoice Paid) instantly update the Consultant System status.

---

## 5. Implementation Phases

| Phase | Title | Focus Area |
| :--- | :--- | :--- |
| **S1** | **Security & Roles** | Define strict Roles (Consultant, Partner) and Permission Rules. |
| **S2** | **Portal Architecture** | Build the navigation structure and basic "My Dashboard" for consultants. |
| **S3** | **Operational Modules** | Port Tasks, Projects, and Deliverables to the new interface. |
| **S4** | **Commercial Modules** | Implement the Contract Builder and Smart Billing interface. |
| **S5** | **HR & Performance** | Build Profile Management and Evaluation systems. |

---

## 6. Next Steps
The immediate next step is to design the **Data Access Layer** and **Role Limitations** to ensure that when we build the new views, the data security is already enforced by the backend.
