# Internship Management System

A full-stack web application designed to streamline the lifecycle of university internship programs, including application submissions, progress tracking via daily logbooks, and multi-tiered supervisor evaluations. Developed as part of the Computer Engineering internship training.

---

## Key Features

- **Role-Based Access Control (RBAC)**: Distinct permissions and views for Students, Company Instructors, University Supervisors, and Administrators.
- **Application Workflow**: Internship posting, student application with CV/document upload, and multi-stage status management (Pending, Approved, Rejected).
- **Logbook Tracking**: Daily work log entry submissions with status monitoring and supervisor approval workflows.
- **Evaluation & Grading**: Standardized evaluation rubrics and grading modules for company mentors and academic supervisors.
- **Resilient UI & Error Boundaries**: Responsive styling, empty-state UI fallbacks, and custom HTTP 404/500 error handlers.

---

## Tech Stack

- **Backend**: Python, Flask, Flask-Login, Werkzeug
- **ORM & Database**: SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
- **Forms & Validation**: WTForms / Email-Validator

---

## Project Structure

```text
internship-management-system/
│
├── app/
│   ├── static/             # CSS stylesheets, static assets, uploaded documents
│   ├── templates/          # Jinja2 templates and role-based views
│   │   └── errors/         # Custom 404 and 500 error pages
│   ├── __init__.py         # Flask app factory and extensions initialization
│   ├── models.py           # SQLAlchemy database entities
│   └── routes.py           # Blueprint endpoints and RBAC guards
│
├── docs/                   # System requirements and technical specifications
├── config.py               # Application configuration settings
├── requirements.txt        # Pinned Python package dependencies
├── run.py                  # Application entry point
└── seed_database.py        # Automated idempotent database seeder