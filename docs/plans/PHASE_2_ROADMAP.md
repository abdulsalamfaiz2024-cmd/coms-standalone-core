# COMS Phase 2: System Intelligence & Automation
**Status:** Draft
**Version:** 2.0

## Executive Summary
Phase 1 established the secure core, database structure, and functional frontend. Phase 2 focuses on **Logic, Automation, and Reporting**. The goal is to transform the system from a "Passive Data Recorder" into an "Active Operational Tool".

---

## 1. Module A: Advanced Reporting & Documents
**Objective:** Enable the system to produce professional, external-facing documents.

*   **A.1 PDF Generation Engine**
    *   **Technology:** `fpdf` or `weasyprint` (Python).
    *   **deliverables:**
        *   Client Invoice PDF (Auto-calculated taxes/totals).
        *   Consultant Contract PDF (Dynamic text replacement).
        *   Project Status Report PDF.
    *   **UI:** "Print to PDF" button on Detail pages.

*   **A.2 Data Export Suite**
    *   **Function:** Export Lists (Clients, Time Logs) to CSV/Excel.
    *   **Use Case:** Finance team needs end-of-month data for payroll.

---

## 2. Module B: Workflow Automation
**Objective:** Reduce manual clicking by chaining events.

*   **B.1 Intelligent Status Logic**
    *   If `Project` status = "Completed" → Check if any `Tasks` are open (Prevent closure).
    *   If `Assignment` created → Auto-deduct hours from `Consultant Availability`.

*   **B.2 Approval Workflows**
    *   **Timesheets:** Consultant submits → Status "Pending" → Manager Approves → Status "Billable".
    *   **Expenses:** Limit auto-approval to < $100. Higher amounts require "Manager" role approval.

---

## 3. Module C: Communication Layer
**Objective:** Keep users informed without checking the system constantly.

*   **C.1 Email Notification System**
    *   **Triggers:**
        *   New User Account created (Welcome Email).
        *   You have been assigned to Task X.
        *   Invoice Overdue alert.
    *   **Tech:** SMTP integration in `server.py`.

*   **C.2 In-App Notifications**
    *   **UI:** Notification Bell in Navbar.
    *   **Backend:** `Notifications` table to store unread alerts.

---

## 4. Module D: Visual Enhancements (UI/UX)
**Objective:** Improve usability for high-volume users.

*   **D.1 Drag-and-Drop Kanban Board**
    *   **Feature:** Manage Tasks by dragging cards between columns (To Do -> doing -> Done).
    *   **Tech:** HTML5 Drag & Drop API in `enterprise_engine.js`.

*   **D.2 Calendar Scheduling View**
    *   **Feature:** Visual timeline of Consultant assignments to spot gaps/overlaps.

---

## 5. Execution Order
1.  **Reporting (A):** High value, immediate client need.
2.  **UI/UX (D):** High visibility, improves user buy-in.
3.  **Automation (B):** Reduces admin burden.
4.  **Communication (C):** Final polish.
