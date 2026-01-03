# Phase S2-A: Portal Foundation (The Shell)

**Document Version:** 1.0
**Created:** 2025-12-30
**Status:** Planning
**Objective:** Deploy the base technical infrastructure for the Consultant Portal. This phase focuses purely on **Access** and **Layout**, ensuring a user can log in and see the empty portal shell.

---

## PART 1: SCOPE & DELIVERABLES

**Goal:** "Get it on the screen."

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **Route `/portal`** | Accessible URL that overrides standard desk. |
| 2 | **Authentication Guard** | Redirects to `/login` if not logged in; Redirects to `/desk` if not a Consultant. |
| 3 | **Base Layout** | HTML structure with Left Sidebar and Top Header (hardcoded menu for now). |
| 4 | **Styling** | Basic CSS/Tailwind setup. |

---

## PART 2: IMPLEMENTATION FILES

| # | File Path | Purpose |
|---|-----------|---------|
| 1 | `d:\erpnext\coms\consulting\www\portal\__init__.py` | Route Init |
| 2 | `d:\erpnext\coms\consulting\www\portal\index.py` | Security Logic (The Guard) |
| 3 | `d:\erpnext\coms\consulting\www\portal\index.html` | The Visual Shell |
| 4 | `d:\erpnext\coms\public\css\portal_style.css` | Styling |

---

## PART 3: DETAILED CODE SPEC

### 3.1 The Visual Shell (`index.html`)

A focused version of the previous plan—just the container, no dynamic JS router yet.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>COMS Consultant Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Essential Overrides */
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 text-gray-800">
    <div class="flex h-screen">
        <!-- STATIC SIDEBAR (Proof of Concept) -->
        <aside class="w-64 bg-white border-r">
            <div class="h-16 flex items-center justify-center border-b">
                <span class="text-xl font-bold text-blue-600">COMS</span>
            </div>
            <div class="p-4">
                <div class="bg-blue-50 text-blue-700 p-2 rounded">Dashboard</div>
                <div class="opacity-50 mt-2 p-2">Projects (Locked)</div>
                <div class="opacity-50 mt-2 p-2">Tasks (Locked)</div>
            </div>
        </aside>

        <!-- MAIN CONTENT -->
        <main class="flex-1 flex flex-col">
            <header class="h-16 bg-white border-b flex items-center px-6">
                <h1 class="text-lg font-semibold">Welcome, Consultant</h1>
            </header>
            <div class="p-6">
                <!-- SUCCESS MESSAGE -->
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                    <strong class="font-bold">Success!</strong>
                    <span class="block sm:inline">The Portal Shell is active and accessible.</span>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
```

### 3.2 The Guard (`index.py`)

Strict security check to ensure we don't accidentally expose this to the wrong users.

```python
import frappe

def get_context(context):
    # 1. No Cache (Development Mode)
    context.no_cache = 1
    
    # 2. Login Check
    if frappe.session.user == 'Guest':
        frappe.local.flags.redirect_location = '/login'
        raise frappe.Redirect
    
    # 3. Role Check (Requires Phase S1 completion)
    # allowed_roles = ["Consultant", "Administrator"]
    # if not any(r in frappe.get_roles() for r in allowed_roles):
    #     frappe.local.flags.redirect_location = '/desk'
    #     raise frappe.Redirect
    
    context.user = frappe.utils.get_fullname(frappe.session.user)
```

---

## PART 4: EXECUTION STEPS

1.  **Delete** any existing `www/portal` folder to ensure clean slate.
2.  **Create** the 4 files above.
3.  **Visit** `[site-url]/portal` in browser.
4.  **Verify** you see the Green Success Message.
