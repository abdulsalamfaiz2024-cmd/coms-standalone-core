# Phase S4: Commercial Modules User Interface (Contracts & Finance)

**Document Version:** 1.0
**Created:** 2025-12-30
**Status:** Planning
**Objective:** Create the "Read-Only" Financial and Contractual dashboards for the Consultant Portal. This phase focuses on **transparency**—giving consultants visibility into their legal agreements and payment status without giving them access to the accounting ledger.

---

## PART 1: PHILOSOPHY - "THE DASHBOARD"

Unlike Phase S3 (which involved *Inputs* like Time Logs), Phase S4 is primarily about **Visualizing Data**.

| Module | Goal | Source Logic (Build) |
|--------|------|----------------------|
| **Contracts** | "What did we agree to?" | `COMS_Phase2` (Client/Consultant Contract) |
| **Finance** | "When do I get paid?" | `COMS_Phase5` (Invoicing/Profitability) |

---

## PART 2: IMPLEMENTATION FILES

We will organize these modules as Javascript components loaded into the Portal App.

| # | File Path | Purpose | Linking to Backend File |
|---|-----------|---------|-------------------------|
| 1 | `d:\erpnext\coms\consulting\www\portal\js\contract.js` | Contract Viewer Class | `client_contract.py` |
| 2 | `d:\erpnext\coms\consulting\www\portal\js\finance.js` | Financial Status Charts | `invoice_generator.py` |

---

## PART 3: DETAILED VIEW SPECIFICATIONS

### 3.1 Module E: Contracts Hub (Read-Only)

**Goal:** Provide a clean, summarized view of the Active Contract, separating the "Legalese" from the "Terms".

**Backend Integration:**
*   **Source:** Fetch `Client Contract` linked to the Project.
*   **Filter:** `row_level_security.py` ensures consultants only see contracts for *their* projects.

**Key Features (The Mirror):**
*   **Milestone Tracker:** A progress bar showing `Milestones Completed` vs `Total Milestones` (Data from `Contract Milestone` table).
*   **Terms Summary:** Clean display of "Hourly Rate", "Start Date", "End Date".
*   **Documents:** List of attached PDF contracts available for download.

**HTML Component:**
```html
<div class="contract-viewer">
    <div class="header flex justify-between">
        <h2>Contract #{naming_series}</h2>
        <span class="badge badge-green">{status}</span>
    </div>
    
    <div class="grid grid-cols-2 gap-6 mt-4">
        <div class="card p-4">
            <h4 class="text-gray-500">Value</h4>
            <p class="text-2xl font-bold">{contract_value}</p>
        </div>
        <div class="card p-4">
            <h4 class="text-gray-500">Type</h4>
            <p class="text-xl">{contract_type}</p>
        </div>
    </div>
    
    <!-- Milestone Progress -->
    <div class="mt-6">
        <h3>Milestones</h3>
        <ul id="milestone-list">
            <!-- JS Injected: <li><check> Milestone A - $500 - [Completed]</li> -->
        </ul>
    </div>
</div>
```

### 3.2 Module F: Finance Center (Read-Only)

**Goal:** Answer the question "Have I been paid?" without exposing the Company General Ledger.

**Backend Integration:**
*   **Source:** Queries `Sales Invoice` (for Client Billing) and potentially `Purchase Invoice` or `Payment Entry` (if Consultant is external).
*   **Logic:** Uses `profitability.py` logic (Phase 5B) to show project financial health *if allowed*.

**Key Features (The Mirror):**
*   **My Earnings:** (For Freelancers) Chart of "Logged Hours x Rate" vs "Paid Amount".
*   **Project Budget:** (For Managers) "Budget vs Actual" consumption gauge.
*   **Invoices:** List of invoices raised for this project and their payment status (Paid/Unpaid/Overdue).

**JS Representation:**
```javascript
async function loadFinance(projectId) {
    // API Call to S1 Backend
    let financialData = await frappe.call("coms.consulting.api.consultant_api.get_project_finance", { project: projectId });
    
    // Render Chart using Frappe Charts or Chart.js
    new Chart("#finance-chart", {
        data: financialData.revenue_vs_cost,
        type: 'bar'
    });
}
```

---

## PART 4: REQUIRED API WRAPPERS

We need to add these "Read-Only" fetchers to `consultant_api.py`.

| API Method | Wraps Existing Logic | Data Returned |
|------------|----------------------|---------------|
| `get_my_contracts` | Queries `Client Contract` & `Contract Milestone` | List of contracts + milestones |
| `get_project_finance` | Queries `Sales Invoice` & `Timesheet` | Aggregate totals (Billed, Paid, Pending) |

---

## PART 5: EXECUTION CHECKLIST

**To Deploy Phase S4:**
1.  [ ] Create `contract.js` and `finance.js`.
2.  [ ] Implement the `get_my_contracts` and `get_project_finance` methods in the API (S1).
3.  [ ] **TEST:** Login -> Click "Contracts" -> Verify Milestones match the backend.
4.  [ ] **TEST:** Login -> Click "Finance" -> Verify "Invoiced Amount" matches the Sales Invoices in Desk.

---
**End of Phase S4 Plan**
