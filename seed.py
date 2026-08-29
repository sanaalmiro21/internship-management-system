from datetime import date, datetime, timezone
from app import create_app, db
from app.models import (
    User,
    University,
    Student,
    Company,
    CompanyInstructor,
    UniversitySupervisor,
    Application,
    Internship,
    Document,
    Evaluation,
    Admin,
)

app = create_app()

with app.app_context():
    # 1. Reset database tables
    db.drop_all()
    db.create_all()
    print("Database tables initialized.")

    # 2. Create University User & Profile
    uni_user = User(
        username="uni_admin",
        email="contact@karabuk.edu.tr",
        password="hashed_password_123",
        role="university",
    )
    db.session.add(uni_user)
    db.session.flush()

    university = University(
        university_id=uni_user.user_id,
        university_name="Karabuk University",
        department="Computer Engineering",
    )
    db.session.add(university)

    # 3. Create Student User & Profile
    student_user = User(
        username="student_sana",
        email="sana@example.com",
        password="hashed_password_123",
        role="student",
    )
    db.session.add(student_user)
    db.session.flush()

    student = Student(
        student_id=student_user.user_id,
        university_id=uni_user.user_id,
        student_number="2310213589",
        first_name="Sana",
        last_name="Almiro",
        department="Computer Engineering",
    )
    db.session.add(student)

    # 4. Create Company User & Profile
    comp_user = User(
        username="tech_corp",
        email="hr@techcorp.com",
        password="hashed_password_123",
        role="company",
    )
    db.session.add(comp_user)
    db.session.flush()

    company = Company(
        company_id=comp_user.user_id,
        company_name="TechCorp Solutions",
        address="Ankara, Turkey",
        website="https://techcorp.example.com",
    )
    db.session.add(company)

    # 5. Create Company Instructor & University Supervisor
    instructor = CompanyInstructor(
        company_id=comp_user.user_id,
        first_name="Murat",
        last_name="Demir",
        position="Senior Lead Engineer",
        phone="+905551112233",
    )
    supervisor = UniversitySupervisor(
        university_id=uni_user.user_id,
        first_name="Ahmet",
        last_name="Yilmaz",
        position="Associate Professor",
        phone="+905554445566",
    )
    db.session.add_all([instructor, supervisor])
    db.session.flush()

    # 6. Create Application (Student applies to Company)
    application = Application(
        student_id=student.student_id,
        company_id=company.company_id,
        position="Software Engineering Intern",
        cover_letter="I am enthusiastic about building web systems with Python and Flask.",
        status="Accepted",
    )
    db.session.add(application)
    db.session.flush()

    # 7. Create Internship (from Accepted Application)
    internship = Internship(
        application_id=application.application_id,
        student_id=student.student_id,
        title="Backend Software Internship",
        description="Internship focused on Flask API development and database architecture.",
        start_date=date(2026, 8, 17),
        end_date=date(2026, 9, 11),
        status="Ongoing",
    )
    db.session.add(internship)
    db.session.flush()

    # 8. Create Document & Evaluations
    doc = Document(
        internship_id=internship.internship_id,
        file_name="weekly_log_week1.pdf",
        file_path="uploads/internships/1/weekly_log_week1.pdf",
        document_type="Logbook",
        uploaded_by=student_user.user_id,
    )

    eval_company = Evaluation(
        internship_id=internship.internship_id,
        instructor_id=instructor.instructor_id,
        score=95.0,
        comment="Strong understanding of backend architectures and Git versioning.",
        evaluation_type="Company",
    )

    db.session.add_all([doc, eval_company])
    db.session.commit()

    print("--- Verification Queries ---")
    print(f"Student: {student.first_name} {student.last_name}")
    print(f"Enrolled University: {student.university.university_name}")
    print(f"Application Status: {student.applications[0].status}")
    print(f"Active Internship: {student.internships[0].title}")
    print(f"Company Evaluation Score: {internship.evaluations[0].score}")
    print("Database seeding & relationship testing completed successfully.")
    