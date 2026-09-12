from datetime import date, datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import (
    User, Student, Company, University, Admin,
    CompanyInstructor, UniversitySupervisor,
    InternshipListing, Application, Internship,
    LogbookEntry, Evaluation
)

app = create_app()

def seed():
    with app.app_context():
        print("Resetting database schema...")
        db.drop_all()
        db.create_all()

        print("1. Creating system administrator...")
        admin_user = User(
            username="admin_sys",
            email="admin@ims.edu",
            password=generate_password_hash("Admin123!"),
            role="Admin",
            is_approved=True
        )
        db.session.add(admin_user)
        db.session.flush()

        admin_profile = Admin(
            admin_id=admin_user.user_id,
            first_name="System",
            last_name="Administrator",
            admin_level="SuperAdmin"
        )
        db.session.add(admin_profile)

        print("2. Creating University and Academic Supervisor...")
        uni_user = User(
            username="karabuk_uni",
            email="coordinator@karabuk.edu.tr",
            password=generate_password_hash("Uni123!"),
            role="University",
            is_approved=True
        )
        db.session.add(uni_user)
        db.session.flush()

        university = University(
            university_id=uni_user.user_id,
            university_name="Karabük University",
            department="Computer Engineering"
        )
        db.session.add(university)
        db.session.flush()

        uni_supervisor = UniversitySupervisor(
            university_id=university.university_id,
            first_name="Ahmet",
            last_name="Yilmaz",
            position="Assistant Professor / Internship Coordinator",
            phone="+90 370 418 8000"
        )
        db.session.add(uni_supervisor)

        print("3. Creating Company and Industry Instructor...")
        comp_user = User(
            username="techcorp_solutions",
            email="supervisor@techcorp.com",
            password=generate_password_hash("Comp123!"),
            role="Company",
            is_approved=True
        )
        db.session.add(comp_user)
        db.session.flush()

        company = Company(
            company_id=comp_user.user_id,
            company_name="TechCorp Solutions",
            address="Technopark, Maslak, Istanbul",
            website="https://techcorp.example.com"
        )
        db.session.add(company)
        db.session.flush()

        comp_instructor = CompanyInstructor(
            company_id=company.company_id,
            first_name="Murat",
            last_name="Demir",
            position="Principal Software Architect / Mentor",
            phone="+90 555 019 2831"
        )
        db.session.add(comp_instructor)

        print("4. Creating Students...")
        stu_user_1 = User(
            username="sana_almiro",
            email="sana@student.karabuk.edu.tr",
            password=generate_password_hash("Student123!"),
            role="Student",
            is_approved=True
        )
        db.session.add(stu_user_1)
        db.session.flush()

        student_1 = Student(
            student_id=stu_user_1.user_id,
            university_id=university.university_id,
            student_number="20220101",
            first_name="Sana",
            last_name="Almiro",
            department="Computer Engineering"
        )
        db.session.add(student_1)

        # Neutral completed test persona for academic evaluation verification
        stu_user_2 = User(
            username="ali_kaya",
            email="ali.kaya@student.karabuk.edu.tr",
            password=generate_password_hash("Student123!"),
            role="Student",
            is_approved=True
        )
        db.session.add(stu_user_2)
        db.session.flush()

        student_2 = Student(
            student_id=stu_user_2.user_id,
            university_id=university.university_id,
            student_number="20220102",
            first_name="Ali",
            last_name="Kaya",
            department="Computer Engineering"
        )
        db.session.add(student_2)
        db.session.commit()

        print("5. Creating Listing & Placement Applications...")
        listing = InternshipListing(
            company_id=company.company_id,
            title="Full-Stack Web Engineering Intern",
            department="Engineering",
            location="Hybrid / Istanbul",
            description="Developing backend routes in Flask, relational schema architecture, and UI templates.",
            requirements="Python, SQL, HTML/CSS",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=15),
            required_hours=240.0,
            is_active=True
        )
        db.session.add(listing)
        db.session.flush()

        app_1 = Application(
            student_id=student_1.student_id,
            company_id=company.company_id,
            listing_id=listing.listing_id,
            position=listing.title,
            cover_letter="Interested in backend database modeling and web security.",
            status="Accepted"
        )
        app_2 = Application(
            student_id=student_2.student_id,
            company_id=company.company_id,
            listing_id=listing.listing_id,
            position=listing.title,
            cover_letter="Looking to fulfill my graduation practical requirements.",
            status="Accepted"
        )
        db.session.add_all([app_1, app_2])
        db.session.commit()

        print("6. Creating Internships & Evaluations...")
        # Active ongoing internship for primary student
        active_internship = Internship(
            application_id=app_1.application_id,
            student_id=student_1.student_id,
            company_id=company.company_id,
            listing_id=listing.listing_id,
            start_date=listing.start_date,
            end_date=listing.end_date,
            required_hours=240.0,
            status="Ongoing"
        )
        db.session.add(active_internship)

        # Completed & graded internship for secondary reference test
        completed_internship = Internship(
            application_id=app_2.application_id,
            student_id=student_2.student_id,
            company_id=company.company_id,
            listing_id=listing.listing_id,
            start_date=date.today() - timedelta(days=90),
            end_date=date.today() - timedelta(days=10),
            required_hours=240.0,
            status="Approved",
            grade="AA",
            evaluation_notes="Completed all technical milestones with distinction.",
            evaluated_by=university.university_id,
            evaluated_at=datetime.now(timezone.utc)
        )
        db.session.add(completed_internship)
        db.session.commit()

        # Link Company Instructor & University Supervisor evaluations
        comp_eval = Evaluation(
            internship_id=completed_internship.internship_id,
            instructor_id=comp_instructor.instructor_id,
            score=95.0,
            comment="Outstanding software design skills and fast turnaround.",
            evaluation_type="Company"
        )
        uni_eval = Evaluation(
            internship_id=completed_internship.internship_id,
            supervisor_id=uni_supervisor.supervisor_id,
            score=98.0,
            comment="Academic report and logbook entries fully verified.",
            evaluation_type="University"
        )
        db.session.add_all([comp_eval, uni_eval])

        print("7. Seeding Logbook Entries...")
        log1 = LogbookEntry(
            internship_id=active_internship.internship_id,
            entry_date=date.today() - timedelta(days=2),
            hours_worked=8.0,
            tasks_performed="Configured relational schema, applied foreign keys and table constraints.",
            learnings="SQLAlchemy table relationship mapping and cascades.",
            status="Approved",
            supervisor_feedback="Solid work on relational constraints.",
            reviewed_at=datetime.now(timezone.utc)
        )
        log2 = LogbookEntry(
            internship_id=active_internship.internship_id,
            entry_date=date.today() - timedelta(days=1),
            hours_worked=8.0,
            tasks_performed="Built logbook submission endpoints.",
            learnings="Form handling in Flask.",
            status="Needs Revision",
            supervisor_feedback="Please elaborate on validation rules applied to input dates."
        )
        log3 = LogbookEntry(
            internship_id=active_internship.internship_id,
            entry_date=date.today(),
            hours_worked=8.0,
            tasks_performed="Implemented error handlers (404/500) and styled empty dashboard views.",
            learnings="Defensive UX design.",
            status="Pending"
        )
        db.session.add_all([log1, log2, log3])
        db.session.commit()

        print("Database seeded successfully with all relationships intact.")

if __name__ == "__main__":
    seed()