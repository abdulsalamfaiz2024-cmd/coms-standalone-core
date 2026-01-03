# Phase S5: Master Data Integration & Form Linkage
**Objective:** Connect the "Placeholder" modules (Clients, Consultants, Employees) and the "Operational" modules (Projects, Tasks) to live backend data and forms.

## 1. Plan Overview
This phase moves the portal from "Static/Mock" to "Dynamic/Connected". We will implement read-only directories for Master Data and detail views for forms.

## 2. API Implementation (`consultant_api.py`)
We will add the following read-only wrappers. **Privacy is key:** Consultants only see what they are allowed to see.

### A. Clients (`get_my_clients`)
- **Logic:** Fetch `Customer` records linked to the consultant's active `Projects`.
- **Security:** Strict Row-Level Security. Consultant X only sees Client Y if they are assigned to a Project for Client Y.

### B. Consultants (`get_consultant_directory`)
- **Logic:** Fetch public profiles of *other* consultants.
- **Security:** Public directory data only (Name, Expertise, Bio - NO rates/contracts).
- **Purpose:** "Find an Expert" feature.

### C. Employees (`get_team_members`)
- **Logic:** Fetch internal employees (Project Managers, Partners) assigned to the consultant's projects.
- **Security:** Only show team members relevant to active work.

## 3. Frontend Implementation (`www/portal/js/`)
We will create dedicated JS modules for these views, moving logic out of `app.js`.

- `client.js`: Grid view of Clients -> Click to see "Client Card" (Address, Key Contacts).
- `consultant_module.js`: Directory view -> Click to see "Bio/Expertise".
- `employee.js`: Team list -> Click to see "Contact Info".

## 4. Form Linkage (The "Deep Dive")
We will implement the "Drill-Down" capability:
- **Project List** -> Click -> **Project Detail View** (Scope, Milestones, Team).
- **Client List** -> Click -> **Client Detail View**.

## 5. Execution Steps
1. [ ] Add API endpoints to `consultant_api.py`.
2. [ ] Create JS modules (`client.js`, `consultant_module.js`, `employee.js`).
3. [ ] Update `app.js` to load these modules instead of placeholders.
4. [ ] Restart Docker to apply backend changes.
