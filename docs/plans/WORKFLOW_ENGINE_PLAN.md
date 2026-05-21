# Consulting System Workflow Architecture
**Based on Industry Best Practices**

## 1. Executive Summary
This document outlines the **Workflow Engine** specifications tailored for a high-end consulting firm. The workflows are designed to ensure distinct Quality Assurance (QA) layers, proper billing authorization, and risk management.

## 2. Core Workflow Schemas

### A. The "Engagement" Workflow (Projects)
**Philosophy:** Projects are not just "Open/Closed"; they move through a commercial lifecycle.
*   **States:**
    1.  `Prospect` (Proposal stage, 10% probability)
    2.  `Active` (Contract signed, billable work starts)
    3.  `In Review` (Final deliverables submitted, billing paused)
    4.  `Completed` (Client sign-off received, archived)
*   **Transitions:**
    *   `Prospect` → `Active`: Requires "Contract Upload". (Role: Partner)
    *   `Active` → `Completed`: Requires "Final Invoice" generated. (Role: Manager)

### B. The "Billable Hour" Workflow (Timesheets)
**Philosophy:** Time = Money. Every hour must be vetted before the client sees the bill.
*   **States:**
    1.  `Draft` (Consultant logging daily hours)
    2.  `Submitted` (Locked for Consultant, visible to PM)
    3.  `PM Approved` (Validated against project budget)
    4.  `Invoiced` (Billed to client, strictly locked)
*   **Transitions:**
    *   `Draft` → `Submitted`: End of Week. (Role: Consultant)
    *   `Submitted` → `PM Approved`: Verify work description. (Role: Manager/Partner)
    *   `PM Approved` → `Invoiced`: Auto-transition when Invoice created. (System)

### C. The "Standard of Care" Workflow (Deliverables)
**Philosophy:** Nothing goes to the client without a "Four-Eyes" review.
*   **States:**
    1.  `Work in Progress` (Drafting)
    2.  `Internal Review` (Peer check / Sr. Consultant check)
    3.  `Partner QA` (Final brand/risk check)
    4.  `Client Ready` (Approved for sharing)
*   **Transitions:**
    *   `WIP` → `Internal Review`: (Role: Consultant)
    *   `Internal Review` → `Partner QA`: (Role: Manager)
    *   `Partner QA` → `Client Ready`: (Role: Partner)

## 3. Implementation Strategy (The Engine)

### 3.1 Data Structure (`backend/workflows/definitions.py`)
We will define these rules in a central Python dictionary to allow easy modification.

```python
WORKFLOW_DEFINITIONS = {
    "Deliverable": {
        "states": ["WIP", "Internal Review", "Partner QA", "Client Ready"],
        "transitions": [
            {
                "action": "Submit for Review",
                "from_state": "WIP",
                "to_state": "Internal Review",
                "allowed_roles": ["Consultant", "Manager"]
            },
            {
                "action": "Approve (Internal)",
                "from_state": "Internal Review",
                "to_state": "Partner QA",
                "allowed_roles": ["Manager", "Partner"]
            },
            {
                "action": "Final Authorization",
                "from_state": "Partner QA",
                "to_state": "Client Ready",
                "allowed_roles": ["Partner"]
            },
            {
                "action": "Reject / Revise",
                "from_state": ["Internal Review", "Partner QA"],
                "to_state": "WIP",
                "allowed_roles": ["Manager", "Partner"]
            }
        ]
    }
}
```

### 3.2 The API (`server.py` extensions)
*   `POST /api/workflow/transition`: Universal endpoint to move any document.
    *   **Payload:** `{ doctype: "Deliverable", id: "123", action: "Approve" }`
    *   **Logic:**
        1.  Fetch Document.
        2.  Check current state.
        3.  Look up valid transitions in `definitions.py`.
        4.  Verify User Role.
        5.  **Execute Update** & **Log in Interaction History**.

## 4. Next Steps
1.  **Code the Engine:** Create `System_Core/backend/workflow_engine.py`.
2.  **Define Rules:** Create `System_Core/backend/workflows.py` with the schemas above.
3.  **UI Update:** Replace static Status dropdowns with dynamic Workflow Actions in `enterprise_engine.js`.
