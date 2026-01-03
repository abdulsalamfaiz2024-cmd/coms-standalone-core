# Docker Activation Guide for COMS System Separation

Since you are running ERPNext in Docker, you cannot run `bench` commands directly from your Windows PowerShell. You must execute them **inside** the container or restart the container to pick up the changes.

## 1. Applying the Python Changes (Phase S1 & S4 APIs)
The Python files (`consultant_api.py`, etc.) have been created on your disk, but the running Docker container has loaded the *old* code in memory.

### Option A: Restart the Container (Easiest)
Run this in your terminal:
```bash
docker restart <your-frappe-container-name>
```

### Option B: Restart Bench Inside Docker
If you have access to the container shell:
1.  Enter the container:
    ```bash
    docker exec -it <container-name> bash
    ```
2.  Restart the python process:
    ```bash
    bench restart
    ```

## 2. Applying the Database Changes (Security Roles)
Phase S1 required creating new Roles (`Consultant`, `Consulting Partner`). Using `bench execute` is the standard way, but in Docker, it's safer to use the **Web Interface** if you can't run scripts easily.

**Manual Verification Steps (Web UI):**
1.  Login to ERPNext as **Administrator**.
2.  Go to **Role List**.
3.  Verify if `Consultant` and `Consulting Partner` exist.
4.  If not, create them manually.

## 3. Verifying the Portal (Phase S2-S4)
The Portal files are located in `www/portal`.
*   **HTML/JS changes:** These should be visible **immediately** upon refreshing your browser (no restart needed for `www` files usually).
*   **API Calls (`get_my_dashboard` etc.):** These will FAIL until you perform **Step 1 (Restart)**.

### Troubleshooting API Errors
If you click "Projects" and see the "Mock Data" warning:
1.  Check your browser console (F12).
2.  If you see `404 Not Found` for `.../api/method/coms.consulting.api...`:
    *   It means the **Python Code** hasn't reloaded. **Restart the container.**
3.  If you see `403 Forbidden`:
    *   It means **Permissions** aren't applied. Ensure your User has the `Consultant` role.

---
**Summary:**
1.  **RESTART** your Docker container now.
2.  **REFRESH** the browser.
3.  **TEST** the Portal.
