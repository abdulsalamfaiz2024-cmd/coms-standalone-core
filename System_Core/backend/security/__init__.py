# -*- coding: utf-8 -*-
# Copyright (c) 2025, COMS
# License: MIT

"""
COMS Security Module
====================

This module provides security infrastructure for the Consultant Portal:
- Role definitions and management
- Permission matrix configuration
- Row-level security filters
- Document-level permission handlers

Part of Phase S1: Security & Roles Implementation
"""

from backend.security.roles import COMS_ROLES, get_role_config
from backend.security.permissions import PERMISSION_MATRIX, get_permissions_for_role
from backend.security.row_level_security import (
    get_consultant_employee_id,
    get_consultant_projects,
    apply_project_filter,
    apply_task_filter,
    apply_deliverable_filter,
    apply_timesheet_filter
)

__all__ = [
    "COMS_ROLES",
    "get_role_config",
    "PERMISSION_MATRIX",
    "get_permissions_for_role",
    "get_consultant_employee_id",
    "get_consultant_projects",
    "apply_project_filter",
    "apply_task_filter",
    "apply_deliverable_filter",
    "apply_timesheet_filter"
]
