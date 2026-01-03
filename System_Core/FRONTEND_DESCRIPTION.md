# Consultancy OS - Frontend Architecture Description

This document describes the structure and design of the independent, relational frontend system.

## 1. Architectural Overview
The frontend is a **Modular Relational Interface** designed to be completely independent of any external framework. It uses a "Page-Injection" model where a central shell (`index.html`) dynamically loads specific HTML modules from the disk based on the user's navigation.

## 2. Directory Structure
All frontend files are located in: `d:\Custom_System_Copy\System_Core\frontend\portal\`

```text
portal/
├── index.html          # The Main Enterprise Shell (Sidebar, Header, Breadcrumbs)
├── css/
│   └── style.css       # Design System (Typography, Colors, Layout Constraints)
├── js/
│   └── core.js         # The Modular Controller (Data fetching, SQL commits, Page routing)
└── pages/              # Independent Page Modules
    ├── list.html                   # Generic data grid fallback
    ├── form.html                   # Universal SQL record editor
    ├── clients.html                # Custom Strategic Clients view
    ├── consultants.html            # Custom Expert Directory view
    ├── consultancy_assignments.html # Custom Project Management view
    └── client_invoices.html        # Custom Financial Tracking view
```

## 3. Key Component Descriptions

### **A. The Shell (index.html)**
Acts as the "Command Center." It maintains the persistent Sidebar and Top Bar. It contains the logic to watch the URL hash (e.g., `#Consultants`) and trigger the `core.js` engine to load the correct module.

### **B. The Data Engine (js/core.js)**
The "Brain" of the interface. Its responsibilities are:
1.  **Routing**: Maps URL hashes to physical `.html` files in the `pages/` folder.
2.  **Schema Fetching**: Queries the `/api/meta` endpoint to understand the SQL table structure.
3.  **Relational Rendering**: Merges the HTML templates with real-time data from the SQLite database.
4.  **SQL Commits**: Handles the submission of forms directly to the relational backend.

### **C. The Model System (pages/form.html)**
A high-fidelity modal interface that builds dynamic forms based on the database schema. It ensures that data entered by the user is correctly mapped to SQL columns before being saved.

### **D. The Design System (css/style.css)**
A professional enterprise theme using the **Plus Jakarta Sans** typeface. It features:
*   **Fixed Layout**: Prevents overlapping of sidebars and content.
*   **Visual Hierarchy**: Uses badges for IDs, pills for statuses, and soft-shadowed cards for data groups.
*   **Responsive Grids**: Automatically organizes form inputs into a clean 2-column layout.

## 4. Data Flow Path
1.  **Navigation**: User clicks "Consultants" -> Hash changes to `#Consultants`.
2.  **Template Load**: `core.js` fetches `pages/consultants.html`.
3.  **Data Fetch**: `core.js` performs parallel `GET` requests to `/api/meta` and `/api/list`.
4.  **Render**: Data is injected into the table within the consultants template.
5.  **Write**: User edits a record -> `core.js` performs a `POST` to `/api/save` -> Record is committed to `consultancy.db`.

---
*Created for the Independent Consultancy OS Relational v2.0*
