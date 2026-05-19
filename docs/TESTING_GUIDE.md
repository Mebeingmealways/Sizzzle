# Testing Guide

This repository deliverable set includes backend API tests only.

## Test Assets in This Repository

- Backend tests: `docs/testing/backend/`
- Test matrix YAML: `docs/testing/test-matrix.yaml`

## Backend Test Run

Prerequisites:
- Python 3.10+
- Virtual environment activated

Commands:

```bash
cd backend
python -m pytest tests -v
```

Alternative using docs copies:

```bash
cd backend
python -m pytest ../docs/testing/backend -v
```

## Test Scope

- Authentication and role access
- Profile and preference flows
- Booking lifecycle and cancellation rules
- Manager and admin dashboards
- Notifications and unread state transitions

## Expected Result

All backend tests should pass without external cloud dependencies when run against local SQLite test fixtures.
