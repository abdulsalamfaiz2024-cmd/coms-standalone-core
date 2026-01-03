# -*- coding: utf-8 -*-
# Copyright (c) 2025, COMS
# License: MIT

"""
COMS API Module
===============

Provides secure API endpoints for the Consultant Portal.
All endpoints use @frappe.whitelist() and respect row-level security.

Part of Phase S1: Security & Roles Implementation
"""

from backend.api.consultant_api import (
    get_my_dashboard,
    get_my_tasks,
    get_my_timesheets,
    get_my_deliverables,
    get_my_projects,
    get_my_profile
)

__all__ = [
    "get_my_dashboard",
    "get_my_tasks",
    "get_my_timesheets",
    "get_my_deliverables",
    "get_my_projects",
    "get_my_profile"
]
