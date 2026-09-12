# Software Requirements Specification (SRS)

## Internship Management System (IMS)

---

## 1. Introduction

### 1.1 Purpose

This document presents the Software Requirements Specification (SRS) for the **Internship Management System (IMS)**.

The IMS is a full-stack web application developed to manage the university internship lifecycle. The system provides role-based functionality for students, company instructors, university supervisors, and system administrators.

This document describes the implemented system requirements, user roles, functional requirements, non-functional requirements, system architecture, security considerations, and major workflows.

### 1.2 Scope

The Internship Management System provides a centralized platform for managing internship activities from internship opportunity creation through application processing, internship progress tracking, daily logbook submission, supervision, evaluation, and final grading.

The system provides functionality for:

* User registration and authentication
* Role-based access control
* Internship opportunity management
* Student internship applications
* Supporting document uploads
* Application status management
* Daily internship logbooks
* Company instructor supervision
* University supervisor supervision
* Company evaluations
* University evaluations and grading
* Administrative management
* Form validation
* Error handling

---

# 2. System Architecture

The application follows a modular Flask architecture using the **Application Factory pattern**, Flask routes, SQLAlchemy ORM, Jinja2 templates, and a relational database.

```text
┌─────────────────────────────────────────────┐
│              Client Browser                 │
│       HTML5 / CSS3 / JavaScript             │
└──────────────────────┬──────────────────────┘
                       │
                 HTTP (Development)
                       │
                       ▼
┌─────────────────────────────────────────────┐
│          Flask Application                  │
│                                             │
│  Routes / Authentication / RBAC / Logic     │
└───────────────┬─────────────────┬───────────┘
                │                 │
                ▼                 ▼
┌────────────────────────┐  ┌─────────────────┐
│    SQLAlchemy ORM      │  │ Jinja2 Templates│
└────────────┬───────────┘  └─────────────────┘
             │
             ▼
┌─────────────────────────────┐
│       SQLite Database       │
└─────────────────────────────┘
```

### 2.1 Development and Production Transport

The application is currently run locally over standard HTTP using Flask's development server:

```text
http://127.0.0.1:5000
```

HTTPS/TLS is not terminated by the local Flask development server.

For a production deployment, HTTPS/TLS can be provided by a reverse proxy or load balancer, such as Nginx, Caddy, or a cloud load balancer, while the Flask application operates behind that infrastructure.

### 2.2 Technology Stack

| Component            | Technology                |
| -------------------- | ------------------------- |
| Programming Language | Python                    |
| Web Framework        | Flask                     |
| Authentication       | Flask-Login               |
| ORM                  | SQLAlchemy                |
| Database             | SQLite                    |
| Templates            | Jinja2                    |
| Frontend             | HTML5, CSS3, JavaScript   |
| Forms                | Flask-WTF / WTForms       |
| Email Validation     | Email-Validator           |
| Password Security    | Werkzeug password hashing |
| Version Control      | Git / GitHub              |

### 2.3 Application Structure

```text
app/
├── __init__.py       # Flask application factory
├── models.py         # SQLAlchemy database models
├── routes.py         # Routes and access control
├── templates/        # Jinja2 templates
└── static/           # CSS, JavaScript, and uploaded files

config.py             # Application configuration
run.py                # Application entry point
seed_database.py      # Database seeding
requirements.txt      # Python dependencies
docs/                 # Technical documentation
```

---

# 3. User Roles and Permission Matrix

The system implements Role-Based Access Control (RBAC).

| System Feature / Operation     | Student | Company Instructor | University Supervisor | System Admin |
| ------------------------------ | :-----: | :----------------: | :-------------------: | :----------: |
| Account Registration           |    ✓    |          ✓         |           —           |       —      |
| Create Internship Listings     |    —    |          ✓         |           —           |       ✓      |
| Manage Internship Listings     |    —    |          ✓         |           —           |       ✓      |
| Browse Internship Listings     |    ✓    |          ✓         |           ✓           |       ✓      |
| Submit Internship Applications |    ✓    |          —         |           —           |       —      |
| Upload Application Documents   |    ✓    |          —         |           —           |       —      |
| Review Applications            |    —    |          ✓         |           —           |       ✓      |
| Submit Daily Logbook Entries   |    ✓    |          —         |           —           |       —      |
| Review Daily Logbooks          |    —    |          ✓         |           ✓           |       ✓      |
| Submit Company Evaluation      |    —    |          ✓         |           —           |       ✓      |
| Submit University Evaluation   |    —    |          —         |           ✓           |       ✓      |
| Manage Users                   |    —    |          —         |           —           |       ✓      |
| Administrative Management      |    —    |          —         |           —           |       ✓      |

---

# 4. Functional Requirements

## 4.1 Authentication and Account Management

### FR-01 — Account Registration

The system allows supported users to create accounts by providing the required registration information.

### FR-02 — Password Security

User passwords are never stored as plaintext.

The application uses Werkzeug's `generate_password_hash` functionality to generate cryptographically salted password hashes before storing credentials in the database.

The exact hashing algorithm is determined by the installed Werkzeug version. Werkzeug versions may use different secure default algorithms, such as PBKDF2 or scrypt.

### FR-03 — User Authentication

Users can authenticate using their registered credentials and terminate their authenticated session through the logout functionality.

### FR-04 — Session Management

Flask-Login manages authenticated user sessions and provides access to the current authenticated user.

### FR-05 — Role-Based Authorization

Protected routes check the authenticated user's role before allowing access to role-specific functionality.

---

# 5. Internship Management Requirements

### FR-06 — Internship Creation

Authorized company instructors and administrators can create internship opportunities.

Internship information can include relevant details such as:

* Title
* Description
* Location
* Duration
* Requirements
* Available capacity

### FR-07 — Internship Management

Authorized users can manage internship opportunities according to their assigned permissions.

### FR-08 — Internship Browsing

Students can browse available internship opportunities and inspect their details.

---

# 6. Application Management Requirements

### FR-09 — Application Submission

Students can submit applications for available internship opportunities.

### FR-10 — Supporting Documents

Students can upload required supporting documents as part of the application process.

### FR-11 — Application Status

Applications support status tracking, including:

* Pending
* Approved
* Rejected

### FR-12 — Application Review

Authorized company instructors and administrators can review submitted applications and update their status.

### FR-13 — Internship Association

Approved applications are associated with the corresponding internship workflow and student records.

---

# 7. Daily Logbook Requirements

### FR-14 — Daily Logbook Submission

Students can submit daily records describing their internship work and activities.

### FR-15 — Logbook Information

Logbook records can contain information such as:

* Date
* Work performed
* Hours worked
* Skills or competencies developed
* Submission status

### FR-16 — Logbook Review

Company instructors and university supervisors can review student logbook submissions according to their permissions.

### FR-17 — Logbook Status

Logbook records can be monitored according to their current review status.

---

# 8. Evaluation and Grading Requirements

### FR-18 — Company Evaluation

Company instructors can submit evaluations of student internship performance.

### FR-19 — University Evaluation

University supervisors can review student performance and submit the academic evaluation.

### FR-20 — Final Assessment

The system supports the completion of the internship evaluation process through company and university assessment components.

---

# 9. Document Management Requirements

### FR-21 — Supported File Types

The application validates uploaded documents according to the file types supported by the system.

Supported document formats include:

* `.pdf`
* `.docx`

### FR-22 — Secure Filename Handling

Uploaded filenames are processed using Werkzeug's `secure_filename` utility to reduce risks associated with unsafe filenames and path traversal.

### FR-23 — Document Storage

Uploaded documents are stored in the application's designated upload location and associated with the relevant system records.

### FR-24 — Request Size Limitation

The application limits incoming HTTP request payloads to a maximum of **16 MB** using Flask's `MAX_CONTENT_LENGTH` configuration.

This limit helps prevent excessively large requests and provides an additional protection against resource exhaustion caused by oversized uploads.

# 10. Error Handling and Validation

### FR-25 — HTTP Error Handling

The application provides custom error handling for common HTTP errors, including:

* HTTP 404 — Resource Not Found
* HTTP 500 — Internal Server Error

### FR-26 — Form Validation

Submitted forms are validated before being processed.

### FR-27 — Empty-State Handling

The interface provides informative empty-state messages when requested records or dashboard data are unavailable.

---

# 11. Non-Functional Requirements

## 11.1 Security

### Password Protection

Passwords are securely hashed using Werkzeug's password-hashing functionality before database storage.

### Authentication

Flask-Login provides authenticated session management.

### Authorization

Role-based access checks prevent users from accessing functionality outside their assigned permissions.

### SQL Injection Protection

Database operations are performed through SQLAlchemy ORM functionality rather than relying on dynamically constructed SQL queries.

### Cross-Site Scripting Protection

Jinja2 provides automatic HTML escaping for normal template variables, helping reduce the risk of XSS when user-controlled values are rendered.

### File Upload Security

Uploaded filenames are sanitized using `secure_filename`, and the application restricts uploaded files to supported document formats.

---

# 12. Data Integrity

The application uses SQLAlchemy ORM and relational database relationships to associate related records.

Primary-key and foreign-key relationships are used to maintain relationships between relevant entities.

Database operations are performed through SQLAlchemy database sessions and transactions.

SQLite foreign-key enforcement and relationship-level cascading behavior depend on the configuration implemented in the application and database models.

---

# 13. Usability Requirements

The system provides:

* Role-specific interfaces
* Clear navigation
* Form validation feedback
* Informative error messages
* Empty-state messages
* Custom error pages
* Responsive layouts
* Consistent user interface components

The application is intended to be accessible through modern desktop and mobile web browsers.

---

# 14. Maintainability Requirements

The application separates major responsibilities into independent modules.

| Component          | Responsibility                               |
| ------------------ | -------------------------------------------- |
| `app/models.py`    | Database models and relationships            |
| `app/routes.py`    | Routes, request handling, and access control |
| `app/templates/`   | User interface                               |
| `app/static/`      | CSS, JavaScript, and static resources        |
| `config.py`        | Application configuration                    |
| `seed_database.py` | Database initialization and demo data        |

This modular organization improves maintainability and allows individual components to be modified without unnecessarily affecting other parts of the application.

---

# 15. Main System Workflows

## 15.1 Internship Application Workflow

```text
Company Instructor
        │
        ▼
Create Internship Listing
        │
        ▼
Student Browses Listings
        │
        ▼
Student Submits Application
        │
        ▼
Application Pending
        │
        ├───────────────┐
        ▼               ▼
    Approved         Rejected
        │
        ▼
Internship Workflow
Begins
```

## 15.2 Internship Progress Workflow

```text
Internship Begins
        │
        ▼
Student Submits Daily Logbook
        │
        ▼
Company Instructor /
University Supervisor Review
        │
        ▼
Internship Progress Monitoring
        │
        ▼
Final Evaluations
        │
        ▼
Final Academic Assessment
```

---

# 16. Database Requirements

The system uses **SQLAlchemy ORM** with **SQLite** as its database engine.

The database architecture is centered around the `USER` entity and role-specific entities.

The user specialization includes:

```text
                    USER
                      │
                 Exclusive ARC
          ┌───────────┼───────────┐
          │           │           │
       STUDENT     COMPANY    UNIVERSITY
                      │
                    ADMIN
```

The final database includes entities supporting:

* Users and roles
* Students
* Companies
* Universities
* Company instructors
* University supervisors
* Internship opportunities
* Applications
* Internship records
* Daily logbook entries
* Documents
* Evaluations
* Grading

The complete entity relationships and cardinalities are documented in the project's ERD/database documentation.

---

# 17. Transport and Deployment Requirements

## Development Environment

The application is executed locally using Flask's development server:

```text
http://127.0.0.1:5000
```

The development environment uses standard HTTP.

## Production Environment

A production deployment should use HTTPS/TLS.

TLS termination can be handled by infrastructure such as:

* Nginx
* Caddy
* AWS Application Load Balancer
* Another production reverse proxy or load balancer

The Flask application itself does not provide production TLS termination in the current development configuration.

---

# 18. System Constraints

The current implementation has the following constraints:

* SQLite is used as the database engine.
* The application requires Python and its listed dependencies.
* Supported document uploads are restricted to the file types implemented by the application.
* System functionality depends on the authenticated user's role.
* The application is accessed through a web browser.
* Production HTTPS requires appropriate deployment infrastructure.
* Incoming request payloads are limited to 16 MB.
---

# 19. Installation and Execution Requirements

### Clone the Repository

```bash
git clone https://github.com/sanaalmiro21/internship-management-system.git
cd internship-management-system
```

### Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Initialize Demo Data

```bash
python seed_database.py
```

### Run the Application

```bash
python run.py
```

The application is then available at:

```text
http://127.0.0.1:5000
```

---

# 20. Project Status

**Status: Completed**

The Internship Management System has been fully implemented as a functional full-stack web application.

The completed system includes:

* ✓ User authentication
* ✓ Role-Based Access Control
* ✓ Student functionality
* ✓ Company Instructor functionality
* ✓ University Supervisor functionality
* ✓ Administrator functionality
* ✓ Internship management
* ✓ Internship applications
* ✓ Document uploads
* ✓ Application status management
* ✓ Daily logbook tracking
* ✓ Supervisor review
* ✓ Company evaluations
* ✓ University evaluations
* ✓ Final grading
* ✓ Form validation
* ✓ Error handling
* ✓ Responsive user interface
* ✓ Database seeding
* ✓ SQLAlchemy ORM
* ✓ SQLite database
* ✓ Git/GitHub version control
* ✓ Technical documentation

---

# 21. References

1. Grinberg, M. (2018). *Flask Web Development: Developing Web Applications with Python*. 2nd Edition. O'Reilly Media.

2. ISO/IEC/IEEE 29148:2018. *Systems and Software Engineering — Life Cycle Processes — Requirements Engineering*.

3. OWASP Foundation. *OWASP Top 10: The Ten Most Critical Web Application Security Risks*.

4. SQLAlchemy Documentation. *SQLAlchemy 2.0 Documentation*.

5. Flask Documentation. *Flask Web Development Framework Documentation*.

6. Flask-Login Documentation. *User Session Management for Flask Applications*.

---

## Document Information

| Field          | Value                                |
| -------------- | ------------------------------------ |
| Project        | Internship Management System         |
| Document       | Software Requirements Specification  |
| Version        | 1.0                                  |
| Status         | Final                                |
| Project Status | Completed                            |
| Technology     | Python / Flask / SQLAlchemy / SQLite |
