# Phase S3: Operational Modules User Interface

**Document Version:** 1.0
**Created:** 2025-12-30
**Status:** Planning
**Objective:** Create the specialized **Frontend Interfaces** (HTML/JS) for Projects, Tasks, Sessions, and Deliverables. These interfaces will run inside the Portal Shell (S2) and strict interact with the **Existing Backend** built in Phases 1-6.

---

## PART 1: PHILOSOPHY - "THE MIRROR"

This phase does **NOT** build new tables. It mirrors existing data into a Consultant-friendly format.

| Existing Doctype (The Source) | Portal Interface (The Mirror) | Interaction Type |
|-------------------------------|-------------------------------|------------------|
| **Project** | `Project Detail View` | Read-Only (Dashboard) |
| **Task** | `Task Board` & `Detail` | Read + Status Update |
| **Timesheet** | `Session Logger` | Create (Log Time) |
| **Deliverable** | `Submission Hub` | Create + Upload |

---

## PART 2: IMPLEMENTATION FILES

We will organize these modules as **Vue.js Components** or **standard JS Bundles** loaded into the main Portal App.

| # | File Path | Purpose | Linking to Backend File |
|---|-----------|---------|-------------------------|
| 1 | `d:\erpnext\coms\consulting\www\portal\js\project.js` | Project Dashboard Logic | `COMS_Phase3A_Project_Enhancements` |
| 2 | `d:\erpnext\coms\consulting\www\portal\js\task.js` | Task Logic & Workflow | `COMS_Phase3B_Task_Workflow` |
| 3 | `d:\erpnext\coms\consulting\www\portal\js\session.js` | Time Logging Logic | `COMS_Phase3C_Timesheet_Integration` |
| 4 | `d:\erpnext\coms\consulting\www\portal\js\deliverable.js` | File Upload Logic | `COMS_Phase4A_Deliverable_Doctype` |

---

## PART 3: DETAILED VIEW SPECIFICATIONS

### 3.1 Module A: Project Intelligence (Read-Only)

**Goal:** Provide the consultant with a "Cockpit" view of the project without exposing financial margins or internal comments.

**HTML Structure (Injected into `#page-content`):**
```html
<div id="project-header" class="bg-white p-6 rounded shadow mb-6">
    <h1 class="text-2xl font-bold">{project_name}</h1>
    <div class="grid grid-cols-4 gap-4 mt-4">
        <div class="stat-box">Status: <span class="badge">{status}</span></div>
        <div class="stat-box">Progress: {percent_complete}%</div>
        <div class="stat-box">Your Role: {consultant_role}</div> <!-- Fetched from Project Consultant Table -->
        <div class="stat-box">Ends In: {days_remaining} Days</div>
    </div>
</div>
<!-- Tabs handled by S2 Router -->
<div id="project-tabs" class="border-b">
    <button onclick="loadTab('tasks')" class="active">Tasks</button>
    <button onclick="loadTab('team')">Team</button>
    <button onclick="loadTab('files')">Files</button>
</div>
```

**Backend Integration:**
*   Calls `get_project_details(project_id)`.
*   **Security:** Only shows if user is in `Project Consultant` child table (Row-Level Security S1).

### 3.2 Module B: Task Execution (Read/Write)

**Goal:** A focused view for the consultant to see "What do I need to do?" and update the status.

**Key Logic:**
*   **Workflow Trigger:** When user clicks "Start Work", JS calls `frappe.call('frappe.model.workflow.apply_workflow', { doc: 'Task', action: 'Start Work' })`.
*   **Availability:** Uses logic from `task_events.py` (Phase 3B) to validate assignment.

**HTML Component:**
```html
<div class="task-card">
    <div class="flex justify-between">
        <h3>{subject}</h3>
        <button class="btn-primary" onclick="updateTaskStatus('{name}', 'In Progress')">Start</button>
    </div>
    <p class="description">{description}</p>
    <hr>
    <div class="actions">
        <button onclick="app.routes.sessions('{name}')">Log Time</button>
        <button onclick="app.routes.deliverables('{name}')">Upload Output</button>
    </div>
</div>
```

### 3.3 Module C: Session Management (Timesheets)

**Goal:** A simplified "Stopwatch" or "Log" interface that creates complex `Timesheet` records in the background.

**The "Magic" Wrapper:**
The form is simple: `[ Date | Hours | Description ]`.
The Backend (`timesheet_events.py`) handles the complexity:
*   Auto-links `Consultant Contract`.
*   Auto-calculates `Billing Rate` (based on Seniority/Contract).
*   Auto-sets `Billable` flag.

**JS Handling:**
```javascript
async function submitSession(taskId, hours, description) {
    await frappe.call({
        method: "coms.consulting.api.consultant_api.log_session",
        args: {
            task: taskId,
            hours: hours,   // Mapped to "total_hours"
            activity: "Consulting",
            description: description
        }
    });
}
```

### 3.4 Module D: Deliverable Hub (The Output)

**Goal:** The standard interface for uploading work.

**Integration with Phase 4A (Deliverable Doctype):**
*   **Form:** Dropzone for file upload.
*   **Action:** Creates a new `Deliverable` doc OR adds a row to `Deliverable Revision` child table if updating.
*   **Workflow:** Clicking "Submit for Review" triggers the `Deliverable Approval Workflow` (Draft -> Submitted).

---

## PART 4: REQUIRED API WRAPPERS

We need to explicitly expose these actions in `consultant_api.py` (S1) to support these views.

| API Method | Wraps Existing Logic |
|------------|----------------------|
| `update_task_status` | `frappe.model.workflow.apply_workflow` |
| `log_session` | `frappe.new_doc("Timesheet").save()` |
| `upload_deliverable` | `frappe.get_doc("Deliverable").save()` |

---

## PART 5: EXECUTION CHECKLIST

**To Deploy Phase S3:**
1.  [ ] Create the JS files in `.../www/portal/js/`.
2.  [ ] Add the HTML templates to `index.html` (hidden by default) or dynamically load them.
3.  [ ] Update `consultant_api.py` with the 3 wrapper methods above.
4.  [ ] **TEST:** Login as Consultant -> Open Project -> Start Task -> Log Time -> Verification (Check standard Desk to see if Timesheet appeared).

---
**End of Phase S3 Plan**
