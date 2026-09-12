# Internship Management System

A full-stack web application designed to streamline the lifecycle of university internship programs, including internship applications, daily logbook tracking, supervisor approvals, and multi-level evaluations.

Developed as part of the **Computer Engineering internship training**.

---

## Key Features

* **Role-Based Access Control (RBAC)**
  Distinct permissions and views for Students, Company Instructors, University Supervisors, and Administrators.

* **Internship Application Workflow**
  Companies can publish internship opportunities, while students can browse available positions and submit applications with the required documents.

* **Application Status Management**
  Applications support multiple statuses, including **Pending**, **Approved**, and **Rejected**.

* **Document Management**
  Students can upload required internship documents, such as CVs and application-related files.

* **Daily Logbook Tracking**
  Students can submit daily internship work logs and monitor their submission status.

* **Supervisor Approval Workflow**
  Company Instructors and University Supervisors can review and approve students' internship progress and logbook entries.

* **Evaluation & Grading**
  Standardized evaluation modules allow company mentors and academic supervisors to assess student performance and contribute to final grading.

* **Responsive User Interface**
  Responsive layouts with role-specific views and user-friendly navigation.

* **Error Handling**
  Custom HTTP `404` and `500` error pages and fallback states for missing or unavailable content.

---

## Tech Stack

### Backend

* Python
* Flask
* Flask-Login
* Werkzeug

### ORM & Database

* SQLAlchemy
* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Forms & Validation

* Flask-WTF / WTForms
* Email-Validator

### Development Tools

* Git
* GitHub
* Python Virtual Environment (`venv`)

---

## Project Structure

```text
internship-management-system/
│
├── app/
│   ├── static/
│   │   ├── css/                 # CSS stylesheets
│   │   ├── js/                  # JavaScript files
│   │   └── uploads/             # Uploaded documents
│   │
│   ├── templates/
│   │   ├── errors/              # Custom 404 and 500 error pages
│   │   └── ...                  # Jinja2 templates and role-based views
│   │
│   ├── __init__.py              # Flask application factory and extensions
│   ├── models.py                # SQLAlchemy database models
│   └── routes.py                # Application routes and RBAC guards
│
├── docs/                        # System requirements and technical documentation
│
├── config.py                    # Application configuration
├── requirements.txt             # Python package dependencies
├── run.py                       # Application entry point
└── seed_database.py             # Database initialization and sample data seeder
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sanaalmiro21/internship-management-system.git
cd internship-management-system
```

### 2. Set Up the Virtual Environment

#### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize and Seed the Database

Run the database seeder to create the required database records and populate the system with demo data:

```bash
python seed_database.py
```

The seeder is designed to be **idempotent**, meaning it can be executed multiple times without unnecessarily creating duplicate demo records.

### 5. Run the Application

```bash
python run.py
```

Then open the application in your browser:

```text
http://127.0.0.1:5000
```

---

## Demo Accounts

All seeded demo accounts use the default password:

```text
password123
```

| Role                      | Email                       | Access Scope                                                                        |
| ------------------------- | --------------------------- | ----------------------------------------------------------------------------------- |
| **Administrator**         | `admin@system.local`        | Full administrative control, user management, and system monitoring                 |
| **University Supervisor** | `supervisor@university.edu` | Academic reviews, student logbook approval, and final grading                       |
| **Company Instructor**    | `mentor@techcorp.com`       | Internship listings, applicant review, and company evaluations                      |
| **Student**               | `student@university.edu`    | Browse internship listings, submit applications, and maintain daily logbook entries |

---

## Main User Roles

### Student

Students can:

* Browse available internship opportunities
* Submit internship applications
* Upload required documents
* Track application status
* Submit daily logbook entries
* Monitor internship progress
* View evaluation results

### Company Instructor

Company Instructors can:

* Publish internship opportunities
* Review student applications
* Manage internship applicants
* Review student progress
* Approve or review logbook entries
* Complete company-side evaluations

### University Supervisor

University Supervisors can:

* Review student internship applications and progress
* Monitor daily logbook submissions
* Approve or review student work logs
* Evaluate student performance
* Contribute to final internship grading

### Administrator

Administrators can:

* Manage system users
* Manage system-wide data
* Monitor application activity
* Maintain administrative records
* Perform system-level management and auditing

---

## Application Workflow

The general internship lifecycle follows this process:

```text
Company
   │
   ▼
Create Internship Listing
   │
   ▼
Student Browses Available Internships
   │
   ▼
Student Submits Application
   │
   ▼
Application Review
   │
   ├── Rejected
   │
   └── Approved
          │
          ▼
     Internship Begins
          │
          ▼
     Daily Logbook Entries
          │
          ▼
     Supervisor Reviews
          │
          ▼
     Internship Evaluation
          │
          ▼
       Final Grade
```

---
## Database Design

The system uses a relational database architecture designed to support the complete university internship lifecycle.

The core user architecture is based on a `USER` supertype with an exclusive specialization into the following roles:

* `STUDENT`
* `COMPANY`
* `UNIVERSITY`
* `ADMIN`

The system also includes supporting entities for managing internship operations, including:

* `COMPANY_INSTRUCTOR`
* `UNIVERSITY_SUPERVISOR`
* `INTERNSHIP`
* `APPLICATION`
* Daily logbook records
* Evaluation records
* Document records

The database is implemented using **SQLAlchemy ORM** with **SQLite** as the database engine.

The database design supports:

* User authentication and role management
* Internship opportunity management
* Student applications
* Application status tracking
* Document submission
* Daily internship logbooks
* Company instructor supervision
* University supervisor review
* Company and university evaluations
* Final grading and internship completion

---

## System Workflow

The completed system supports the full internship lifecycle:

```text
Company
   │
   ▼
Create Internship Listing
   │
   ▼
Student Browses Internships
   │
   ▼
Student Submits Application
   │
   ▼
Application Review
   │
   ├── Rejected
   │
   └── Approved
          │
          ▼
     Internship Begins
          │
          ▼
     Daily Logbook Entries
          │
          ▼
     Supervisor Review
          │
          ▼
   Company Evaluation
          │
          ▼
 University Evaluation
          │
          ▼
       Final Grade
```

---

## Completed Features

The project has been fully implemented and includes the following functionality:

### Authentication & Authorization

* User authentication and login
* Secure password handling
* Role-based access control (RBAC)
* Role-specific dashboards and permissions
* Protected routes based on user roles

### Internship Management

* Creation and management of internship opportunities
* Internship listing and browsing
* Student application submission
* Application document uploads
* Application status management
* Application review by authorized users

### Daily Logbook

* Daily internship work-log submission
* Logbook status tracking
* Supervisor review and approval
* Internship progress monitoring

### Evaluation & Grading

* Company instructor evaluations
* University supervisor evaluations
* Standardized evaluation criteria
* Student performance assessment
* Final grading workflow

### Administration

* User management
* Role management
* System data management
* Administrative monitoring and auditing

### Validation & Error Handling

* Form validation
* Email validation
* Secure file handling
* Custom `404` error page
* Custom `500` error page
* Empty-state handling
* User-friendly error messages

### User Interface

* Responsive web interface
* Role-specific views
* Jinja2-based templates
* CSS styling
* JavaScript-based interactive functionality
* Responsive and user-friendly navigation

---

## Project Status

**Status: Completed**

The Internship Management System has been fully developed and implemented as a complete full-stack web application.

The completed project includes:

* ✅ Flask backend
* ✅ SQLAlchemy ORM
* ✅ SQLite database
* ✅ Authentication system
* ✅ Role-Based Access Control (RBAC)
* ✅ Internship management
* ✅ Application workflow
* ✅ Document uploads
* ✅ Daily logbook system
* ✅ Supervisor approval workflows
* ✅ Company evaluations
* ✅ University evaluations
* ✅ Final grading
* ✅ Administrative functionality
* ✅ Form validation
* ✅ Error handling
* ✅ Responsive user interface
* ✅ Database seeding
* ✅ Git/GitHub version control
* ✅ Technical documentation

The application is ready to run locally using the setup instructions provided above.
