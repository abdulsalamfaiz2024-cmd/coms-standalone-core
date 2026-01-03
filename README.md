# COMS (Consultant Operations & Management System)

## Overview
The Consultant Operations & Management System (COMS) is a specialized environment designed for consultants, integrated with the ERPNext backend. It separates the operational interface for consultants from the core ERPNext system (HR, Accounting, CRM) to provide a streamlined experience.

## Directory Structure

This repository has been reorganized to support a clean implementation workflow:

- **`coms/`**: The main application source code (Frappe App).
    - `coms/coms/`: Python source package.
    - `coms/public/`: Static assets (JS/CSS).
    - `coms/templates/`: Web templates.

- **`scripts/`**: Setup, migration, and utility scripts.
    - `setup_app.sh`: Main shell script to initialize the app configuration.
    - `phases/`: Implementation scripts corresponding to the project phases (S1, S2, etc.).
    - `utils/`: Maintenance and verification utilities (e.g., `verify_static_files.py`, `system_restore.py`).
    - `legacy/`: Archived versions of setup scripts.

- **`docs/`**: Project documentation and architectural plans.
    - `plans/`: Detailed separation strategy and phase definitions (S1-S5).
    - `images/`: Visual assets and diagrams.

## Setup

To initialize the application configuration:

```bash
./scripts/setup_app.sh
```

## Implementation Phases

The project follows a phased retrieval and separation strategy. Scripts for each phase are located in `scripts/phases/`:

- **Phase S1**: Security & Roles (`s1_create_roles.py`, `s1_apply_permissions.py`)
- **Phase S2**: Portal Architecture
- **Phase S3**: Operational Modules (Projects, Tasks)
- **Phase S4**: Commercial Modules
- **Phase S5**: Master Data Integration

## Development

- **App Config**: `pyproject.toml` is generated during setup.
- **Workflow Scripts**: Key workflow scripts like `create_phase3b_workflow.py` and `create_project_templates.py` are located in `scripts/`.
