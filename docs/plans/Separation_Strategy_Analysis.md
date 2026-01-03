# Separation Strategy Analysis & Integration Map

**Document Version:** 1.0
**Created:** 2025-12-30
**Status:** Analysis & Alignment
**Purpose:** To validate the alignment between the **Implemented Build** (in `Customize the system/`) and the **Proposed Separation Strategy**, ensuring full utilization of the existing ERPNext infrastructure.

---

## 1. STRATEGIC ALIGNMENT

The "Separation" is not a rewrite. It is a **User Interface (UI) Layer** sitting on top of the "Build" you have already implemented.

| Layer | Component | Status | Source |
|-------|-----------|--------|--------|
| **1. Database & Logic** | ERPNext + COMS Custom App | **Implemented** | `Customize the system/` (Phases 1-6) |
| **2. Security Rules** | Roles & Permissions | **Planned (S1)** | `System_Separation_Plans/S1` |
| **3. Interface** | Consultant Portal | **Planned (S2)** | `System_Separation_Plans/S2` |

**Conclusion:** The Separation Plan (S2) is strictly a **consumer** of the Build (Phase 1-6). It duplicates **zero** logic.

---

## 2. COMPONENT MAPPING (Build vs. Portal)

This section maps every screen in the proposed Portal to the exact Doctype and Workflow defined in your Build Plan.

### 2.1 "Projects" Screen
*   **Portal View:** List of Active Projects.
*   **Backend Source:** `Project` Doctype (Standard ERPNext).
*   **Modifications Used:**
    *   Uses `consultant_team` Child Table (from **Build Phase 3A**) to filter visibility.
    *   Displays `deliverables_count` (Custom Field from **Build Phase 3A**).
    *   Reflects `project_category` (Custom Field from **Build Phase 3A**).

### 2.2 "Tasks" Screen
*   **Portal View:** Kanban or List of assigned tasks.
*   **Backend Source:** `Task` Doctype (Standard ERPNext).
*   **Modifications Used:**
    *   **Workflow:** Triggers the *Consulting Task Workflow* (from **Build Phase 3B**) exactly (Open -> Assigned -> In Progress).
    *   **Fields:** Displays `estimated_hours` and `is_billable` (from **Build Phase 3B**).

### 2.3 "Deliverables" Screen
*   **Portal View:** Drag-and-drop submission area.
*   **Backend Source:** `Deliverable` Doctype (New Custom Doc from **Build Phase 4A**).
*   **Modifications Used:**
    *   **Versioning:** Uses `Deliverable Revision` child table (from **Build Phase 4A**).
    *   **Workflow:** Triggers *Deliverable Approval Workflow* (from **Build Phase 4B**) (Draft -> Submitted -> Approved).
    *   **Notifications:** Triggers standard Email Alerts defined in **Build Phase 4B**.

### 2.4 "Sessions" (Timesheets) Screen
*   **Portal View:** Time Logger.
*   **Backend Source:** `Timesheet` Doctype (Standard ERPNext).
*   **Modifications Used:**
    *   **Logic:** Uses `Rate Hierarchy` (Override > Contract > Default) calculated by `timesheet_events.py` (from **Build Phase 3C**).
    *   **Billing:** Entries here populate the `Sales Invoice` generator (from **Build Phase 5A**).

### 2.5 "Contracts" Screen
*   **Portal View:** Read-only view of agreements.
*   **Backend Source:** `Client Contract` & `Consultant Contract` (from **Build Phase 2**).
*   **Modifications Used:**
    *   Displays `Milestones` status (from **Build Phase 5B**).

---

## 3. GAP ANALYSIS & PREPARATION

Before proceeding to Phase S3 (Building the screens), we must verify the "Bridge" between the Build and the Portal.

| Critical Check | Status | Action Required |
|----------------|--------|-----------------|
| **User Linking** | ⚠️ Check | Confirm `Employee` doctype has `User ID` set for all Consultants. (Crucial for `row_level_security.py`). |
| **Workflow API** | ⚠️ Check | Confirm `Workflow` transitions can be triggered via API, not just Desk UI. |
| **File Permissions** | ⚠️ Check | `Deliverable` attachments must be readable by "Consultant" role even if "Private". |

---

## 4. REVISED ROADMAP RECOMMENDATION

Based on the "Implemented Build", the Separation Roadmap should be adjusted:

1.  **Phase S1 (Security):** Apply the Roles/Permissions to the **existing** Doctypes (Build Phase 1-6). *No new doctypes needed.*
2.  **Phase S2 (Portal Shell):** Deploy the `/portal` route.
3.  **Phase S3 (Integration):** Connect the Portal Screens to the **Build Logic**:
    *   *Do not write new logic.*
    *   *Write API Wrappers* that call `coms.consulting.events`.

**Decision:** The "Build" is the Engine. The "Separation" is strictly the Wiring. We are ready to wire.
