# COMS System Architecture

This is a proprietary, standalone system for Consulting Operations.
It is decoupled from external frameworks and runs on its own internal core.

## Directory Layout

*   **`System_Core/`**: The root of the application.
    *   **`backend/`**: Contains all business logic, APIs, and data structures.
    *   **`frontend/`**: Contains the User Interface (HTML/JS).
    *   **`frappe.py`**: The internal System Engine (Shim) that powers the backend logic without external dependencies.
    *   **`main.py`**: The entry point to run the system.

## How to Run

Since the system is now standalone, you do not need Docker or Bench.

1.  Open the `System_Core` directory.
2.  Run the main engine:
    ```bash
    python main.py
    ```

## Independence Strategy

The system uses a local shim (`frappe.py`) to interpret the existing business logic. This ensures that the complex logic in `backend/api/` and `backend/billing/` continues to function logically without needing the heavy external framework or database server attached.
