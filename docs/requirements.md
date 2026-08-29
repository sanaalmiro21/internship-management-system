# Internship Management System — System Requirements Specification (SRS)

## 1. Project Overview
A web-based platform to manage the lifecycle of student internships, connecting Students, Companies, University Supervisors, and System Administrators.

---

## 2. User Roles (Actors)
* **Student:** Browses companies, submits internship applications, uploads required weekly/final documents, and views evaluation scores.
* **Company:** Reviews received applications, approves/rejects candidates, assigns company instructors, and submits performance evaluations.
* **University Supervisor:** Monitors student progress, reviews uploaded internship documents, and submits academic evaluations.
* **Admin:** Manages user accounts, oversees system data, and audits application/internship approvals.

---

## 3. Functional Requirements

### 3.1 Authentication & Profile Management
* **FR-01:** Users must be able to register with email, secure password, and an assigned exclusive role (`Student`, `Company`, `University`, `Admin`).
* **FR-02:** Passwords must be hashed before storage in the database.
* **FR-03:** Users must be able to log in and access a role-specific dashboard.

### 3.2 Application Workflow
* **FR-04:** A student can submit an application to a registered company.
* **FR-05:** An application lifecycle transitions through: `Pending` -> `Accepted` / `Rejected`.
* **FR-06:** An `Accepted` application automatically initiates an `Internship` record.

### 3.3 Internship Tracking & Documents
* **FR-07:** Students can upload internship documents (Logbooks, Insurance sheets, Final Reports).
* **FR-08:** Uploaded documents must track upload date and verification status.

### 3.4 Evaluation System
* **FR-09:** Company instructors must be able to submit a performance evaluation (score and feedback).
* **FR-10:** University supervisors must be able to submit an academic evaluation (score and feedback).

---

## 4. Non-Functional Requirements
* **Security:** Role-based access control (RBAC) to ensure users only view and modify their authorized data.
* **Data Integrity:** Foreign key constraints and non-null validation across all relational entities.
* **Maintainability:** Modular Flask application structure separating routes, models, templates, and configurations.