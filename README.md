<p align="center">
  <img src="frontend/public/iconlogo.png" alt="Sizzzle Logo" width="120" />
</p>

<h1 align="center">Sizzzle</h1>
<p align="center"><strong>Home Cooks. Real Taste.</strong></p>
<p align="center"><strong>Team 106</strong></p>

Sizzzle is a full-stack operations platform for home-cook booking workflows with role-based access for customers, cooks, managers, and admins.

## Team Members (Team 106)

| Initial | Name | Email | Phone | GitHub | Discourse | Preferred Roles |
|---|---|---|---|---|---|---|
| A | Aaryan Choudhary | 23f2003700@ds.study.iitm.ac.in | 9929586989 | @23f2003700 | 23f2003700 | 1) Frontend and Deployment, 2) Code Reviewer |

## Project Details (Jan 2026)

- Milestone 1: Deadline by end of Week 3 (February 22)
- Milestone 2: Deadline by end of Week 5 (March 22)
- Sprint 1 (Milestone 3): Deadline by end of Week 7 (April 5)
- Sprint 2 (Milestone 4): Deadline by end of Week 8 (April 20)
- Milestone 5: Deadline by end of Week 9 (April 20)

## Chosen Problem Statement

### Small Business Operations Platform (Home-Cook Service Domain)

Our team chose the Small Business Operations Platform problem and mapped it to a home-cook service business model.

In this domain, daily operations are often fragmented across calls, chat messages, handwritten notes, and spreadsheets. This leads to missed bookings, weak tracking, delayed complaint handling, and poor visibility for managers and admins.

Sizzzle addresses this by providing a structured platform with role-based workflows and API-first backend design for customers, cooks, managers, and admins.

## What We Built To Solve It

- Customer workflows for registration, login, cook discovery, booking, OTP-based service start, completion, cancellation, and rating.
- Cook workflows for availability, job tracking, live location updates, and earnings visibility.
- Manager workflows for cook verification and complaint handling.
- Admin workflows for platform stats, policy management, manager management, and dispute resolution.
- Centralized notification flows and profile/taste-preference management.
- Automated backend API tests using pytest for critical business logic and role-based access.

Functional expectations include:
- At least two distinct roles
- Interrelated workflows (requests, scheduling, resources, payments/invoices without real payment processing, customer interactions)
- API-first implementation
- Automated tests for critical business logic
- Design for future growth and changing requirements

## Repository Layout

```
.
├── backend/
├── frontend/
├── docs/
└── README.md
```

## Run Options

1. Run locally by cloning this codebase.
2. Use the live deployed application and API.

## Local Run Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Step 1: Clone

```bash
git clone <your-repository-url>
cd sizzle-local
```

### Step 2: Backend (Windows PowerShell)

```powershell
cd backend
python -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bootstrap_data.py
python run.py
```

### Step 3: Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Local URLs:
- Frontend: http://localhost:5173
- Backend: http://localhost:5000
- Swagger UI: http://localhost:5000/api/docs

## Live Deployed Links

### Core Links

- Web App: https://sizzzle.me
- API Root: https://api.sizzzle.me/
- API Docs (Swagger UI): https://api.sizzzle.me/api/docs
- OpenAPI JSON: https://api.sizzzle.me/api/openapi.json
- API Health: https://api.sizzzle.me/api/health
- Project Docs Page: https://api.sizzzle.me/project-docs

<!-- DEPLOYED_ENDPOINTS_START -->
## Deployed API Endpoint Links

The following endpoints are currently deployed on production:

| Method | Path | Deployed URL |
|---|---|---|
| GET | /admin/analytics | https://api.sizzzle.me/api/admin/analytics |
| GET | /admin/disputes | https://api.sizzzle.me/api/admin/disputes |
| PATCH | /admin/disputes/{id} | https://api.sizzzle.me/api/admin/disputes/{id} |
| POST | /admin/disputes/{id}/resolve | https://api.sizzzle.me/api/admin/disputes/{id}/resolve |
| GET | /admin/managers | https://api.sizzzle.me/api/admin/managers |
| POST | /admin/managers | https://api.sizzzle.me/api/admin/managers |
| POST | /admin/managers/{id}/region | https://api.sizzzle.me/api/admin/managers/{id}/region |
| GET | /admin/policies | https://api.sizzzle.me/api/admin/policies |
| PUT | /admin/policies | https://api.sizzzle.me/api/admin/policies |
| PUT | /admin/policies/{id} | https://api.sizzzle.me/api/admin/policies/{id} |
| GET | /admin/stats | https://api.sizzzle.me/api/admin/stats |
| POST | /auth/change-password | https://api.sizzzle.me/api/auth/change-password |
| POST | /auth/forgot-password | https://api.sizzzle.me/api/auth/forgot-password |
| POST | /auth/login | https://api.sizzzle.me/api/auth/login |
| GET | /auth/me | https://api.sizzzle.me/api/auth/me |
| POST | /auth/register | https://api.sizzzle.me/api/auth/register |
| POST | /auth/register/cook | https://api.sizzzle.me/api/auth/register/cook |
| POST | /auth/resend-otp | https://api.sizzzle.me/api/auth/resend-otp |
| POST | /auth/reset-password | https://api.sizzzle.me/api/auth/reset-password |
| POST | /auth/verify-email | https://api.sizzzle.me/api/auth/verify-email |
| GET | /bookings | https://api.sizzzle.me/api/bookings |
| POST | /bookings | https://api.sizzzle.me/api/bookings |
| GET | /bookings/{id} | https://api.sizzzle.me/api/bookings/{id} |
| POST | /bookings/{id}/cancel | https://api.sizzzle.me/api/bookings/{id}/cancel |
| GET | /bookings/{id}/cook-location | https://api.sizzzle.me/api/bookings/{id}/cook-location |
| POST | /bookings/{id}/end | https://api.sizzzle.me/api/bookings/{id}/end |
| POST | /bookings/{id}/rate | https://api.sizzzle.me/api/bookings/{id}/rate |
| POST | /bookings/{id}/start | https://api.sizzzle.me/api/bookings/{id}/start |
| PATCH | /bookings/{id}/status | https://api.sizzzle.me/api/bookings/{id}/status |
| POST | /bookings/{id}/verify-otp | https://api.sizzzle.me/api/bookings/{id}/verify-otp |
| GET | /cooks | https://api.sizzzle.me/api/cooks |
| GET | /cooks/{id} | https://api.sizzzle.me/api/cooks/{id} |
| PUT | /cooks/{id}/availability | https://api.sizzzle.me/api/cooks/{id}/availability |
| PUT | /cooks/availability | https://api.sizzzle.me/api/cooks/availability |
| GET | /cooks/earnings | https://api.sizzzle.me/api/cooks/earnings |
| GET | /cooks/jobs | https://api.sizzzle.me/api/cooks/jobs |
| POST | /cooks/location | https://api.sizzzle.me/api/cooks/location |
| POST | /cooks/recommend | https://api.sizzzle.me/api/cooks/recommend |
| GET | /cooks/recommended | https://api.sizzzle.me/api/cooks/recommended |
| GET | /dishes | https://api.sizzzle.me/api/dishes |
| GET | /dishes/{id} | https://api.sizzzle.me/api/dishes/{id} |
| POST | /dishes/ingredients | https://api.sizzzle.me/api/dishes/ingredients |
| GET | /health | https://api.sizzzle.me/api/health |
| GET | /manager/complaints | https://api.sizzzle.me/api/manager/complaints |
| POST | /manager/complaints | https://api.sizzzle.me/api/manager/complaints |
| PATCH | /manager/complaints/{id} | https://api.sizzzle.me/api/manager/complaints/{id} |
| POST | /manager/complaints/{id}/resolve | https://api.sizzzle.me/api/manager/complaints/{id}/resolve |
| GET | /manager/cook-metrics | https://api.sizzzle.me/api/manager/cook-metrics |
| GET | /manager/cooks | https://api.sizzzle.me/api/manager/cooks |
| GET | /manager/verification-queue | https://api.sizzzle.me/api/manager/verification-queue |
| GET | /manager/verifications/{id} | https://api.sizzzle.me/api/manager/verifications/{id} |
| POST | /manager/verifications/{id} | https://api.sizzzle.me/api/manager/verifications/{id} |
| GET | /manager/verifications/pending | https://api.sizzzle.me/api/manager/verifications/pending |
| PATCH | /manager/verify/{id} | https://api.sizzzle.me/api/manager/verify/{id} |
| GET | /notifications | https://api.sizzzle.me/api/notifications |
| POST | /notifications/{id}/read | https://api.sizzzle.me/api/notifications/{id}/read |
| POST | /notifications/read-all | https://api.sizzzle.me/api/notifications/read-all |
| GET | /notifications/unread-count | https://api.sizzzle.me/api/notifications/unread-count |
| GET | /profile | https://api.sizzzle.me/api/profile |
| PUT | /profile | https://api.sizzzle.me/api/profile |
| POST | /profile/change-password | https://api.sizzzle.me/api/profile/change-password |
| GET | /profile/kitchen-checklist | https://api.sizzzle.me/api/profile/kitchen-checklist |
| PUT | /profile/kitchen-checklist | https://api.sizzzle.me/api/profile/kitchen-checklist |
| GET | /profile/taste | https://api.sizzzle.me/api/profile/taste |
| PUT | /profile/taste | https://api.sizzzle.me/api/profile/taste |
<!-- DEPLOYED_ENDPOINTS_END -->

## Backend API Testing (Python Only)

Run backend API tests:

```bash
cd backend
python -m pytest tests -v
```

Deliverable test artifacts are available in docs:
- docs/TESTING_GUIDE.md
- docs/TEST_CASES.md
- docs/swagger-api.yaml
- docs/testing/test-matrix.yaml
- docs/testing/backend/

## Submission Deliverables

All milestone and sprint deliverable requirements are documented in:
- docs/PROJECT_DELIVERABLES_JAN_2026.md

## Notes

- Sprint documentation is backend API test focused in Python pytest format.

