# Phase S2-B: Navigation & Routing Implementation

**Document Version:** 1.0
**Created:** 2025-12-30
**Status:** Planning
**Objective:** Activate the "Remote Control." Implement the Javascript Router (`app.js`) to handle navigation between the 10 menu items and connect the sidebar to the API.

---

## PART 1: PREREQUISITES
*   **Phase S2-A** must be complete (You must be able to see the Shell).
*   **Phase S1** must be complete (API endpoints must exist).

---

## PART 2: SCOPE & DELIVERABLES

**Goal:** "Make the buttons work."

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **Dynamic Sidebar** | Replace static HTML with JS-rendered menu from `11.png` list. |
| 2 | **Client Router** | `app.js` class that intercepts clicks and swaps content div. |
| 3 | **View Loaders** | 10 Empty JS functions (Placeholders) for each screen. |
| 4 | **Backend Wiring** | Connect `Projects` click -> `get_my_dashboard` API. |

---

## PART 3: IMPLEMENTATION DETAILS

### 3.1 The Router (`app.js`)

This file is the "Brain" of the portal.

```javascript
class PortalApp {
    constructor() {
        this.routes = {
            'projects': () => this.loadWithAPI('get_my_dashboard', this.renderProjects),
            'tasks': () => this.renderPlaceholder('Tasks Module'),
            'sessions': () => this.renderPlaceholder('Time Logs'),
            'deliverables': () => this.renderPlaceholder('Deliverables Hub'),
            'finance': () => this.renderPlaceholder('Finance & Billing'),
            'contracts': () => this.renderPlaceholder('My Contracts'),
            // ... strict mapping to 11.png list
        };
        this.init();
    }
    
    async loadWithAPI(method, renderCallback) {
        // Wiring Logic: Calls the API wrapper from S1
        let r = await frappe.call(`coms.consulting.api.consultant_api.${method}`);
        renderCallback(r.message);
    }
    // ... (rest of router logic)
}
```

### 3.2 The View Renderers

We will define the **Frontend Mapping** here.

| Route | Renders | API Source (S1) |
|-------|---------|-----------------|
| `/portal/projects` | Project Card Grid | `get_my_dashboard` |
| `/portal/tasks` | Kanban Board | `get_my_tasks` |
| `/portal/sessions` | Log Form | *(None yet - S3)* |

---

## PART 4: EXECUTION STEPS

1.  **Modify** `index.html` to remove static sidebar and add `<div id="sidebar-container"></div>`.
2.  **Create** `app.js` with the Router logic.
3.  **Link** `app.js` in `index.html`.
4.  **Test** clicking "Projects" -> Verify it calls the API (Network Tab) and updates the screen.
