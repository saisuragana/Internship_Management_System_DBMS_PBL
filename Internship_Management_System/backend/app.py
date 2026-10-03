from functools import wraps
from urllib.parse import urlparse

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection


app = Flask(__name__)
app.secret_key = "internship_project_secret"


# ===============================================================
# HELPERS
# ===============================================================

def safe_next_url(target):
    if not target:
        return None

    parsed = urlparse(target)

    if (
        parsed.netloc
        or parsed.scheme
        or not target.startswith("/")
    ):
        return None

    return target


@app.template_filter("pretty_date")
def pretty_date(value):

    try:
        return value.strftime("%d %b %Y")
    except AttributeError:
        return value


# ===============================================================
# STUDENT AUTHENTICATION
# ===============================================================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "student_id" not in session:
            flash("Please log in to continue.", "info")

            return redirect(
                url_for(
                    "login",
                    next=request.path
                )
            )

        return view(*args, **kwargs)

    return wrapped


def start_student_session(student_id, name):

    # Remove any previous admin session
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)

    session["student_id"] = student_id
    session["student_name"] = name


def student_logout():

    session.pop("student_id", None)
    session.pop("student_name", None)


# ===============================================================
# ADMIN AUTHENTICATION
# ===============================================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def admin_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return view(*args, **kwargs)

    return wrapped


def start_admin_session():

    # Remove student identity completely
    session.pop("student_id", None)
    session.pop("student_name", None)

    session["admin_logged_in"] = True
    session["admin_username"] = ADMIN_USERNAME


# ===============================================================
# TEMPLATE CONTEXT
# ===============================================================

@app.context_processor
def inject_user():

    student_name = session.get("student_name")

    return {

        # Student
        "logged_in": "student_id" in session,
        "student_name": student_name,
        "student_initial":
            student_name[0].upper()
            if student_name
            else "",

        # Admin
        "admin_logged_in":
            session.get("admin_logged_in", False),

        "admin_username":
            session.get("admin_username")

    }


# ===============================================================
# PUBLIC HOME
# ===============================================================

@app.route("/")
def home():

    stats = {
        "opportunities": 0,
        "organizations": 0,
        "students": 0
    }

    latest = []

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT COUNT(*) AS total FROM opportunity"
        )

        stats["opportunities"] = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM organization"
        )

        stats["organizations"] = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM student"
        )

        stats["students"] = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT
                o.title,
                org.name AS organization_name,
                o.location
            FROM opportunity o
            JOIN organization org
                ON o.organization_id = org.organization_id
            ORDER BY o.start_date
            LIMIT 3
        """)

        latest = cursor.fetchall()

        cursor.close()
        connection.close()

    except Exception:
        pass

    return render_template(
        "index.html",
        stats=stats,
        latest=latest
    )


# ===============================================================
# INTERNSHIP OPPORTUNITIES
# ===============================================================

@app.route("/opportunities")
def opportunities():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            o.*,
            org.name AS organization_name
        FROM opportunity o
        JOIN organization org
            ON o.organization_id = org.organization_id
        ORDER BY o.start_date
    """)

    opportunities_list = cursor.fetchall()

    applied_ids = set()

    if "student_id" in session:

        cursor.execute("""
            SELECT opportunity_id
            FROM application
            WHERE student_id = %s
        """, (session["student_id"],))

        applied_ids = {
            row["opportunity_id"]
            for row in cursor.fetchall()
        }

    cursor.close()
    connection.close()

    return render_template(
        "opportunities.html",
        opportunities=opportunities_list,
        applied_ids=applied_ids
    )


# ===============================================================
# STUDENT LOGIN
# ===============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    next_url = safe_next_url(
        request.args.get("next")
        or request.form.get("next")
    )

    if (
        "student_id" in session
        and request.method == "GET"
    ):

        return redirect(
            next_url
            or url_for("dashboard")
        )

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM student
            WHERE email = %s
        """, (email,))

        student = cursor.fetchone()

        valid = False

        if student:

            password_hash = student.get("password_hash")

            if password_hash:

                valid = check_password_hash(
                    password_hash,
                    password
                )

            elif (
                student.get("password")
                and student["password"] == password
            ):

                valid = True

                write_cursor = connection.cursor()

                write_cursor.execute("""
                    UPDATE student
                    SET password_hash = %s
                    WHERE student_id = %s
                """, (
                    generate_password_hash(password),
                    student["student_id"]
                ))

                connection.commit()
                write_cursor.close()

        cursor.close()
        connection.close()

        if valid:

            start_student_session(
                student["student_id"],
                student["name"]
            )

            flash(
                "Welcome back, "
                + student["name"].split()[0]
                + "!",
                "success"
            )

            return redirect(
                next_url
                or url_for("dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid email or password",
            next_url=next_url
        )

    return render_template(
        "login.html",
        next_url=next_url
    )


# ===============================================================
# STUDENT REGISTRATION
# ===============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form.get("phone", "").strip()
        department = request.form["department"].strip()
        year = request.form["year"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT student_id
            FROM student
            WHERE email = %s
        """, (email,))

        if cursor.fetchone():

            cursor.close()
            connection.close()

            return render_template(
                "register.html",
                error="An account with this email already exists."
            )

        cursor.close()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO student
            (
                name,
                email,
                phone,
                department,
                year,
                password_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            name,
            email,
            phone,
            department,
            year,
            generate_password_hash(password)
        ))

        connection.commit()

        new_id = cursor.lastrowid

        cursor.close()
        connection.close()

        start_student_session(
            new_id,
            name
        )

        flash(
            "Account created. Welcome to InternshipHub!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "register.html"
    )


# ===============================================================
# STUDENT LOGOUT
# ===============================================================

@app.route("/logout")
def logout():

    student_logout()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("home")
    )


# ===============================================================
# STUDENT DASHBOARD
# ===============================================================

@app.route("/dashboard")
@login_required
def dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    student_id = session["student_id"]

    cursor.execute("""
        SELECT
            name,
            email,
            department,
            year
        FROM student
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    if not student:

        student_logout()

        cursor.close()
        connection.close()

        return redirect(
            url_for("login")
        )

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM application
        WHERE student_id = %s
    """, (student_id,))

    applications = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM application
        WHERE student_id = %s
        AND status = 'Approved'
    """, (student_id,))

    approved = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM application
        WHERE student_id = %s
        AND status = 'Shortlisted'
    """, (student_id,))

    shortlisted = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM certificate c
        JOIN assignment ass
            ON c.assignment_id = ass.assignment_id
        JOIN application a
            ON ass.application_id = a.application_id
        WHERE a.student_id = %s
    """, (student_id,))

    certificates = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        student=student,
        applications=applications,
        approved=approved,
        shortlisted=shortlisted,
        certificates=certificates
    )


# ===============================================================
# APPLY FOR INTERNSHIP
# ===============================================================

@app.route(
    "/apply/<int:opportunity_id>",
    methods=["POST"]
)
@login_required
def apply(opportunity_id):

    student_id = session["student_id"]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO application
            (
                student_id,
                opportunity_id,
                application_date,
                status
            )
            VALUES (%s, %s, CURDATE(), 'Applied')
        """, (
            student_id,
            opportunity_id
        ))

        connection.commit()

        flash(
            "Application submitted successfully.",
            "success"
        )

    except Exception:

        connection.rollback()

        flash(
            "You have already applied to this internship.",
            "info"
        )

    cursor.close()
    connection.close()

    return redirect(
        url_for("my_applications")
    )


# ===============================================================
# STUDENT APPLICATIONS
# ===============================================================


@app.route("/applications")
@login_required
def my_applications():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT

            a.application_id,

            o.title,

            org.name AS organization,

            a.application_date,
            a.status,

            ap.approval_date,
            ap.remarks AS approval_remarks,

            ass.assignment_id,
            ass.assigned_date,

            fm.name AS faculty_mentor,

            cs.name AS company_supervisor

        FROM application a

        JOIN opportunity o
            ON a.opportunity_id = o.opportunity_id

        JOIN organization org
            ON o.organization_id = org.organization_id

        LEFT JOIN approval ap
            ON a.application_id = ap.application_id

        LEFT JOIN assignment ass
            ON a.application_id = ass.application_id

        LEFT JOIN faculty_mentor fm
            ON ass.mentor_id = fm.mentor_id

        LEFT JOIN company_supervisor cs
            ON ass.supervisor_id = cs.supervisor_id

        WHERE a.student_id = %s

        ORDER BY
            a.application_date DESC,
            a.application_id DESC
    """, (
        session["student_id"],
    ))

    applications = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "applications.html",
        applications=applications
    )
# ===============================================================
# STUDENT PROGRESS
# ===============================================================

@app.route("/progress")
@login_required
def progress():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            wl.log_id,
            wl.week_no,
            wl.log_date,
            wl.activities,
            wl.hours,
            wl.status,
            o.title AS internship
        FROM weekly_log wl

        JOIN assignment ass
            ON wl.assignment_id = ass.assignment_id

        JOIN application a
            ON ass.application_id = a.application_id

        JOIN opportunity o
            ON a.opportunity_id = o.opportunity_id

        WHERE a.student_id = %s

        ORDER BY o.title, wl.week_no
    """, (
        session["student_id"],
    ))

    logs = cursor.fetchall()

    cursor.close()
    connection.close()

    total_hours = sum(
        float(log["hours"])
        for log in logs
    )

    return render_template(
        "progress.html",
        logs=logs,
        total_hours=total_hours
    )


# ===============================================================
# STUDENT RESULTS
# ===============================================================

@app.route("/results")
@login_required
def results():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.name AS student,
            o.title AS internship,
            org.name AS organization,
            e.evaluator_type,
            e.score,
            e.remarks,
            c.certificate_no,
            c.issue_date

        FROM student s

        JOIN application a
            ON s.student_id = a.student_id

        JOIN assignment ass
            ON a.application_id = ass.application_id

        JOIN opportunity o
            ON a.opportunity_id = o.opportunity_id

        JOIN organization org
            ON o.organization_id = org.organization_id

        LEFT JOIN evaluation e
            ON ass.assignment_id = e.assignment_id

        LEFT JOIN certificate c
            ON ass.assignment_id = c.assignment_id

        WHERE s.student_id = %s

        ORDER BY o.title, e.evaluator_type
    """, (
        session["student_id"],
    ))

    results_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "results.html",
        results=results_list
    )


# ===============================================================
# ADMIN LOGIN
# ===============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            start_admin_session()

            flash(
                "Admin login successful.",
                "success"
            )

            return redirect(
                url_for("admin")
            )

        return render_template(
            "admin_login.html",
            error="Invalid admin username or password."
        )

    return render_template(
        "admin_login.html"
    )


# ===============================================================
# ADMIN LOGOUT
# ===============================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)

    flash(
        "Admin logged out successfully.",
        "info"
    )

    return redirect(
        url_for("admin_login")
    )

# ===============================================================
# ADMIN DASHBOARD
# ===============================================================

@app.route("/admin")
@admin_required
def admin():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    def count(sql, params=None):

        cursor.execute(
            sql,
            params or ()
        )

        return cursor.fetchone()["total"]

    # -----------------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------------

    students = count(
        "SELECT COUNT(*) AS total FROM student"
    )

    organizations = count(
        "SELECT COUNT(*) AS total FROM organization"
    )

    opportunities_count = count(
        "SELECT COUNT(*) AS total FROM opportunity"
    )

    applications_count = count(
        "SELECT COUNT(*) AS total FROM application"
    )

    approved = count("""
        SELECT COUNT(*) AS total
        FROM application
        WHERE status = 'Approved'
    """)

    shortlisted = count("""
        SELECT COUNT(*) AS total
        FROM application
        WHERE status = 'Shortlisted'
    """)

    assignments = count(
        "SELECT COUNT(*) AS total FROM assignment"
    )

    # -----------------------------------------------------------
    # INTERNSHIP OPPORTUNITIES
    # -----------------------------------------------------------

    cursor.execute("""
        SELECT
            o.opportunity_id,
            o.title,
            o.location,
            o.start_date,
            o.end_date,
            o.available_slots,
            org.name AS organization_name
        FROM opportunity o

        JOIN organization org
            ON o.organization_id = org.organization_id

        ORDER BY o.opportunity_id DESC
    """)

    opportunities_list = cursor.fetchall()

    # -----------------------------------------------------------
    # STUDENT APPLICATIONS
    # -----------------------------------------------------------

    cursor.execute("""
        SELECT
            a.application_id,
            s.name AS student_name,
            s.email AS student_email,

            o.title AS internship,
            org.name AS organization,

            a.application_date,
            a.status,

            ap.approval_date,
            ap.remarks AS approval_remarks,

            ass.assignment_id,

            fm.name AS faculty_mentor,
            cs.name AS company_supervisor

        FROM application a

        JOIN student s
            ON a.student_id = s.student_id

        JOIN opportunity o
            ON a.opportunity_id = o.opportunity_id

        JOIN organization org
            ON o.organization_id = org.organization_id

        LEFT JOIN approval ap
            ON a.application_id = ap.application_id

        LEFT JOIN assignment ass
            ON a.application_id = ass.application_id

        LEFT JOIN faculty_mentor fm
            ON ass.mentor_id = fm.mentor_id

        LEFT JOIN company_supervisor cs
            ON ass.supervisor_id = cs.supervisor_id

        ORDER BY
            a.application_date DESC,
            a.application_id DESC
    """)

    applications_list = cursor.fetchall()

    # -----------------------------------------------------------
    # FACULTY MENTORS
    # -----------------------------------------------------------

    cursor.execute("""
        SELECT
            mentor_id,
            name,
            department
        FROM faculty_mentor
        ORDER BY name
    """)

    mentors = cursor.fetchall()

    # -----------------------------------------------------------
    # COMPANY SUPERVISORS
    # -----------------------------------------------------------

    cursor.execute("""
        SELECT
            cs.supervisor_id,
            cs.name,
            cs.email,
            cs.organization_id,
            org.name AS organization_name
        FROM company_supervisor cs

        JOIN organization org
            ON cs.organization_id = org.organization_id

        ORDER BY cs.name
    """)

    supervisors = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin.html",

        students=students,
        organizations=organizations,
        opportunities=opportunities_count,
        applications=applications_count,
        approved=approved,
        shortlisted=shortlisted,
        assignments=assignments,

        opportunities_list=opportunities_list,
        applications_list=applications_list,

        mentors=mentors,
        supervisors=supervisors
    )
# ===============================================================
# ADMIN — UPDATE APPLICATION STATUS
# ===============================================================

@app.route(
    "/admin/application/<int:application_id>/status",
    methods=["POST"]
)
@admin_required
def admin_update_application_status(
    application_id
):

    status = request.form.get(
        "status",
        ""
    ).strip()

    remarks = request.form.get(
        "remarks",
        ""
    ).strip()

    allowed_statuses = {
        "Applied",
        "Shortlisted",
        "Rejected",
        "Approved"
    }

    if status not in allowed_statuses:

        flash(
            "Invalid application status.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        # First update application status
        cursor.execute("""
            UPDATE application
            SET status = %s
            WHERE application_id = %s
        """, (
            status,
            application_id
        ))

        # Keep approval table synchronized
        if status in {
            "Approved",
            "Rejected"
        }:

            cursor.execute("""
                SELECT approval_id
                FROM approval
                WHERE application_id = %s
            """, (
                application_id,
            ))

            existing = cursor.fetchone()

            if existing:

                cursor.execute("""
                    UPDATE approval

                    SET
                        approval_date = CURDATE(),
                        status = %s,
                        remarks = %s

                    WHERE application_id = %s
                """, (
                    status,
                    remarks,
                    application_id
                ))

            else:

                cursor.execute("""
                    INSERT INTO approval
                    (
                        application_id,
                        approval_date,
                        status,
                        remarks
                    )
                    VALUES
                    (
                        %s,
                        CURDATE(),
                        %s,
                        %s
                    )
                """, (
                    application_id,
                    status,
                    remarks
                ))

        elif status in {
            "Applied",
            "Shortlisted"
        }:

            cursor.execute("""
                DELETE FROM approval
                WHERE application_id = %s
            """, (
                application_id,
            ))

        connection.commit()

        flash(
            "Application status updated successfully.",
            "success"
        )

    except Exception as error:

        connection.rollback()

        print(
            "Application status update error:",
            error
        )

        flash(
            "Unable to update application status.",
            "error"
        )

    cursor.close()
    connection.close()

    return redirect(
        url_for("admin")
        + "#applications"
    )

# ===============================================================
# ADMIN — ASSIGN FACULTY MENTOR AND COMPANY SUPERVISOR
# ===============================================================

@app.route(
    "/admin/application/<int:application_id>/assign",
    methods=["POST"]
)
@admin_required
def admin_assign_internship(application_id):

    mentor_id = request.form.get(
        "mentor_id",
        ""
    ).strip()

    supervisor_id = request.form.get(
        "supervisor_id",
        ""
    ).strip()

    if not mentor_id or not supervisor_id:

        flash(
            "Please select both a faculty mentor and company supervisor.",
            "error"
        )

        return redirect(
            url_for("admin")
            + "#applications"
        )

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # -------------------------------------------------------
        # Check application
        # -------------------------------------------------------

        cursor.execute("""
            SELECT
                a.application_id,
                a.status,
                o.organization_id,
                o.title AS internship

            FROM application a

            JOIN opportunity o
                ON a.opportunity_id = o.opportunity_id

            WHERE a.application_id = %s
        """, (
            application_id,
        ))

        application = cursor.fetchone()

        if not application:

            flash(
                "Application not found.",
                "error"
            )

            cursor.close()
            connection.close()

            return redirect(
                url_for("admin")
            )

        # -------------------------------------------------------
        # Only approved applications can be assigned
        # -------------------------------------------------------

        if application["status"] != "Approved":

            flash(
                "Only approved applications can be assigned.",
                "error"
            )

            cursor.close()
            connection.close()

            return redirect(
                url_for("admin")
                + "#applications"
            )

        # -------------------------------------------------------
        # Check mentor exists
        # -------------------------------------------------------

        cursor.execute("""
            SELECT mentor_id
            FROM faculty_mentor
            WHERE mentor_id = %s
        """, (
            mentor_id,
        ))

        mentor = cursor.fetchone()

        if not mentor:

            flash(
                "Selected faculty mentor was not found.",
                "error"
            )

            cursor.close()
            connection.close()

            return redirect(
                url_for("admin")
                + "#applications"
            )

        # -------------------------------------------------------
        # Check company supervisor
        # -------------------------------------------------------

        cursor.execute("""
            SELECT
                supervisor_id,
                organization_id
            FROM company_supervisor
            WHERE supervisor_id = %s
        """, (
            supervisor_id,
        ))

        supervisor = cursor.fetchone()

        if not supervisor:

            flash(
                "Selected company supervisor was not found.",
                "error"
            )

            cursor.close()
            connection.close()

            return redirect(
                url_for("admin")
                + "#applications"
            )

        # -------------------------------------------------------
        # Ensure supervisor belongs to internship organization
        # -------------------------------------------------------

        if (
            supervisor["organization_id"]
            != application["organization_id"]
        ):

            flash(
                "The selected company supervisor does not belong to the internship organization.",
                "error"
            )

            cursor.close()
            connection.close()

            return redirect(
                url_for("admin")
                + "#applications"
            )

        # -------------------------------------------------------
        # Check whether assignment already exists
        # -------------------------------------------------------

        cursor.execute("""
            SELECT assignment_id
            FROM assignment
            WHERE application_id = %s
        """, (
            application_id,
        ))

        existing_assignment = cursor.fetchone()

        if existing_assignment:

            # Update existing assignment

            cursor.execute("""
                UPDATE assignment

                SET
                    mentor_id = %s,
                    supervisor_id = %s

                WHERE application_id = %s
            """, (
                mentor_id,
                supervisor_id,
                application_id
            ))

            message = "Internship assignment updated successfully."

        else:

            # Create new assignment

            cursor.execute("""
                INSERT INTO assignment
                (
                    application_id,
                    mentor_id,
                    supervisor_id,
                    assigned_date
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    CURDATE()
                )
            """, (
                application_id,
                mentor_id,
                supervisor_id
            ))

            message = "Faculty mentor and company supervisor assigned successfully."

        connection.commit()

        flash(
            message,
            "success"
        )

    except Exception as error:

        connection.rollback()

        print(
            "Assignment error:",
            error
        )

        flash(
            "Unable to create internship assignment.",
            "error"
        )

    cursor.close()
    connection.close()

    return redirect(
        url_for("admin")
        + "#applications"
    )
# ===============================================================
# ADMIN — ADD OPPORTUNITY
# ===============================================================

@app.route(
    "/admin/opportunity/add",
    methods=["GET", "POST"]
)
@admin_required
def admin_add_opportunity():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            organization_id,
            name
        FROM organization
        ORDER BY name
    """)

    organizations = cursor.fetchall()

    if request.method == "POST":

        organization_id = request.form[
            "organization_id"
        ]

        title = request.form[
            "title"
        ].strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        start_date = request.form[
            "start_date"
        ]

        end_date = request.form[
            "end_date"
        ]

        available_slots = int(
            request.form[
                "available_slots"
            ]
        )

        if end_date < start_date:

            cursor.close()
            connection.close()

            return render_template(
                "admin_opportunity_form.html",
                organizations=organizations,
                error="End date cannot be earlier than start date."
            )

        if available_slots <= 0:

            cursor.close()
            connection.close()

            return render_template(
                "admin_opportunity_form.html",
                organizations=organizations,
                error="Available slots must be greater than zero."
            )

        cursor.execute("""
            INSERT INTO opportunity
            (
                organization_id,
                title,
                description,
                location,
                start_date,
                end_date,
                available_slots
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            organization_id,
            title,
            description,
            location,
            start_date,
            end_date,
            available_slots
        ))

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Internship opportunity added successfully.",
            "success"
        )

        return redirect(
            url_for("admin")
        )

    cursor.close()
    connection.close()

    return render_template(
        "admin_opportunity_form.html",
        organizations=organizations
    )


# ===============================================================
# ADMIN — EDIT OPPORTUNITY
# ===============================================================

@app.route(
    "/admin/opportunity/edit/<int:opportunity_id>",
    methods=["GET", "POST"]
)
@admin_required
def admin_edit_opportunity(
    opportunity_id
):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM opportunity
        WHERE opportunity_id = %s
    """, (
        opportunity_id,
    ))

    opportunity = cursor.fetchone()

    if not opportunity:

        cursor.close()
        connection.close()

        flash(
            "Internship opportunity not found.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    cursor.execute("""
        SELECT
            organization_id,
            name
        FROM organization
        ORDER BY name
    """)

    organizations = cursor.fetchall()

    if request.method == "POST":

        organization_id = request.form[
            "organization_id"
        ]

        title = request.form[
            "title"
        ].strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        start_date = request.form[
            "start_date"
        ]

        end_date = request.form[
            "end_date"
        ]

        available_slots = int(
            request.form[
                "available_slots"
            ]
        )

        if end_date < start_date:

            cursor.close()
            connection.close()

            return render_template(
                "admin_opportunity_form.html",
                opportunity=opportunity,
                organizations=organizations,
                error="End date cannot be earlier than start date."
            )

        if available_slots <= 0:

            cursor.close()
            connection.close()

            return render_template(
                "admin_opportunity_form.html",
                opportunity=opportunity,
                organizations=organizations,
                error="Available slots must be greater than zero."
            )

        cursor.execute("""
            UPDATE opportunity

            SET
                organization_id = %s,
                title = %s,
                description = %s,
                location = %s,
                start_date = %s,
                end_date = %s,
                available_slots = %s

            WHERE opportunity_id = %s
        """, (
            organization_id,
            title,
            description,
            location,
            start_date,
            end_date,
            available_slots,
            opportunity_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Internship opportunity updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin")
        )

    cursor.close()
    connection.close()

    return render_template(
        "admin_opportunity_form.html",
        opportunity=opportunity,
        organizations=organizations
    )


# ===============================================================
# ADMIN — DELETE OPPORTUNITY
# ===============================================================

@app.route(
    "/admin/opportunity/delete/<int:opportunity_id>",
    methods=["POST"]
)
@admin_required
def admin_delete_opportunity(
    opportunity_id
):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM opportunity
            WHERE opportunity_id = %s
        """, (
            opportunity_id,
        ))

        connection.commit()

        if cursor.rowcount:

            flash(
                "Internship opportunity deleted successfully.",
                "success"
            )

        else:

            flash(
                "Internship opportunity not found.",
                "error"
            )

    except Exception as error:

        connection.rollback()

        print(
            "Opportunity delete error:",
            error
        )

        flash(
            "This internship cannot be deleted because related application records exist.",
            "error"
        )

    cursor.close()
    connection.close()

    return redirect(
        url_for("admin")
    )


# ===============================================================
# RUN APPLICATION
# ===============================================================

if __name__ == "__main__":
    app.run(debug=True)