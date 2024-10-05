from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
from datetime import datetime
import openai
app = Flask(__name__)

# Connecting to the PostgreSQL database
def connect_to_database():
    try:
        conn = psycopg2.connect(
            database="Project MSFEA", user='postgres',
            password='Talineslim0303$', host='localhost', port='5432'
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None

def fetch_entity_tables_data():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            entities = {
                'departments': "SELECT * FROM Departments",
                'students': "SELECT * FROM Students",
                'professors': "SELECT * FROM Professors",
                'courses': "SELECT * FROM Courses",
                'clubs': "SELECT * FROM Clubs",
                'buildings': "SELECT * FROM Buildings",
                'rooms': "SELECT * FROM Rooms",
                'room_bookings': "SELECT * FROM Room_Booking",
                'final_exam_schedules': "SELECT * FROM Final_Exam_Schedule",
                'research_projects': "SELECT * FROM Research_And_Projects",
                'administrative_staff' : "SELECT * FROM Administrative_Staff",
                'student_courses': "SELECT * FROM Student_Courses",
                'research_with_professors': "SELECT * FROM Research_with_professors"


            }
            data = {}
            for key, query in entities.items():
                cursor.execute(query)
                data[key] = cursor.fetchall()
            cursor.close()
            conn.close()
            return data
        except psycopg2.Error as e:
            print("Error fetching entity tables data:", e)
            return None
    else:
        return None

# Create a new function to fetch data from the STUDENT_ENROLLED_CLUB table
def fetch_student_enrolled_clubs():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM STUDENT_ENROLLED_CLUB")
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            return data
        except psycopg2.Error as e:
            print("Error fetching data from STUDENT_ENROLLED_CLUB:", e)
            return None
    else:
        return None

def fetch_departments():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Departments")
            departments_data = cursor.fetchall()
            cursor.close()
            return departments_data
        except psycopg2.Error as e:
            print("Error fetching departments data:", e)
        finally:
            conn.close()
    return []

def fetch_professor_details(professor_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT Professors.Name, COUNT(Students.Student_ID) AS student_count, 
                    ARRAY_AGG(Students.Name) AS advised_students, 
                    ARRAY_AGG(Clubs.Name) AS advised_clubs, 
                    ARRAY_AGG(Courses.Title) AS teaching_courses
                    FROM Professors
                    LEFT JOIN Students ON Professors.Professor_ID = Students.Advisor_ID
                    LEFT JOIN Clubs ON Professors.Professor_ID = Clubs.Faculty_Advisor_ID
                    LEFT JOIN Courses ON Professors.Professor_ID = Courses.Professor_ID
                    WHERE Professors.Professor_ID = %s
                    GROUP BY Professors.Name;
                """, (professor_id,))
                professor_data = cursor.fetchone()
                return professor_data
        except psycopg2.Error as e:
            print(f"Database error while fetching professor details: {e}")
        finally:
            if conn:
                conn.close()
    return None



def fetch_professors_by_department(department_id):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Professors WHERE Department_ID = %s", (department_id,))
            professors_data = cursor.fetchall()
            cursor.close()
            return professors_data
        except psycopg2.Error as e:
            print("Error fetching professors data:", e)
        finally:
            conn.close()
    return []


@app.route('/')
def home():
    image_url = url_for('static', filename='AUB_Campus.jpg')
    return render_template('homepage.html', image_url=image_url)


@app.route('/discover')

def display_all_data():
    # Assuming fetch_entity_tables_data() returns a dictionary of all data
    data = fetch_entity_tables_data()

    if data:
        # Pass the individual data sets to the template. The keys should match your entity names.
        return render_template('discover.html',
                            departments=data['departments'],
                            students=data['students'],
                            professors=data['professors'],
                            courses=data['courses'],
                            clubs=data['clubs'],
                            buildings=data['buildings'],
                            rooms=data['rooms'],
                            room_bookings=data['room_bookings'],
                            final_exam_schedules=data['final_exam_schedules'],
                            research_projects=data['research_projects'],
                            administrative_staff=data['administrative_staff'],
                            student_courses= data['student_courses'],
                            research_with_professors=data['research_with_professors'])
            
    else:
        return render_template('error.html', message="Error fetching data")



@app.route('/about-us')
def about_us():
    return render_template('about_us.html')


def fetch_courses():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT course_id, title FROM Courses")
            courses_data = cursor.fetchall()
            cursor.close()
            conn.close()
            return courses_data
        except psycopg2.Error as e:
            print("Error fetching courses data:", e)
            return None
    else:
        return None
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'POST':
        # Handle POST logic here
        return handle_post_courses()

    # Handle GET request
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT course_id, title FROM Courses")
            courses_data = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('courses.html', courses=courses_data)
        else:
            return render_template('error.html', message="Unable to connect to the database.")
    except psycopg2.Error as e:
        print("Error fetching courses data:", e)
        return render_template('error.html', message="Error fetching courses data")
    except Exception as e:
        print(f"Unexpected error: {e}")
        return render_template('error.html', message="An unexpected error occurred")

def handle_post_courses():
    # Handle POST logic separately for clarity
    student_name = request.form.get('student_name')
    student_id = is_enrolled(student_name)  # Assumes this returns an ID or None
    if student_id is None:
        return "You are not enrolled in the institution. Only enrolled students can register for courses."
    
    selected_courses = request.form.getlist('courses')
    if len(selected_courses) > 5:
        return "You can only register for up to 5 courses. Please select fewer courses and try again."
    
    success = insert_student_courses(student_id, selected_courses)
    if success:
        return "Courses registered successfully!"
    else:
        return render_template('error.html', message="Failed to register courses")

# Note: Add more error handling as needed

def is_enrolled(student_name):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT student_id FROM Students WHERE name = %s", (student_name,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] if result else None  # Returns student_id if found
        except psycopg2.Error as e:
            print("Error checking enrollment status:", e)
            return False
    else:
        return False


def insert_student_courses(student_id, selected_courses):
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Insert new records for the student's selected courses
            cursor.execute("INSERT INTO student_courses (student_id, course_names) VALUES (%s, %s)", (student_id, selected_courses))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except psycopg2.Error as e:
            print("Error inserting student courses:", e)
            return False
    else:
        return False


@app.route('/departments')
def departments():
    departments = fetch_departments()  # Fetch departments from the database
    return render_template('departments.html', departments=departments)



def fetch_departments():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Departments")
            departments_data = cursor.fetchall()
            cursor.close()
            return departments_data
        except psycopg2.Error as e:
            print("Error fetching departments data:", e)
        finally:
            conn.close()
    return []


@app.route('/department_details/<int:department_id>')
def department_details(department_id):
    department_info = get_department_info(department_id)
    professors = get_professors_by_department(department_id)
    staff = get_staff_by_department(department_id)
    student_count = get_student_count_by_department(department_id)
    
    print("Department:", department_info)  # Debug print
    print("Professors:", professors)       # Debug print
    print("Staff:", staff)                 # Debug print
    print("Student Count:", student_count) # Debug print

    return render_template('department_details.html', department=department_info,
                           professors=professors, staff=staff, student_count=student_count)

def get_department_info(department_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Departments WHERE Department_ID = %s", (department_id,))
                department_info = cursor.fetchone()
                return department_info
        except psycopg2.Error as e:
            print(f"Database error while fetching department info: {e}")
        finally:
            if conn:
                conn.close()
    return None

def get_professors_by_department(department_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM Professors WHERE Department_ID = %s
                """, (department_id,))
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Database error while fetching professors: {e}")
        finally:
            if conn:
                conn.close()
    return []

def get_staff_by_department(department_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM Administrative_Staff WHERE Department_ID = %s
                """, (department_id,))
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Database error while fetching staff: {e}")
        finally:
            if conn:
                conn.close()
    return []

def get_student_count_by_department(department_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Adjusting the query to count students directly linked to the department
                cursor.execute("""
                    SELECT COUNT(*) FROM Students WHERE Department_ID = %s
                """, (department_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except psycopg2.Error as e:
            print(f"Database error while fetching student count: {e}")
        finally:
            if conn:
                conn.close()
    return 0

@app.route('/find_people', methods=['GET', 'POST'])
def find_people():
    student_info = None
    all_students = None
    message = None

    # Connect to the database
    conn = connect_to_database()

    # If the method is POST, perform the search
    if request.method == 'POST' and conn:
        student_name = request.form['student_name'].strip()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Students WHERE Name ILIKE %s LIMIT 1", ('%' + student_name + '%',))
            student_record = cursor.fetchone()
            if student_record:
                student_info = {
                    'student_id': student_record[0],
                    'name': student_record[1],
                    'email': student_record[2],
                    'major': student_record[3],
                    'year': student_record[4]
                }
            else:
                message = "This student isn't enrolled at AUB."
            cursor.close()
        except psycopg2.Error as e:
            print("Database error:", e)
            message = "An error occurred while searching for the student."

    # Whether it's a GET or POST request, fetch all students to display
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Students")
            all_students = cursor.fetchall()
            cursor.close()
        except psycopg2.Error as e:
            print("Database error when fetching all students:", e)
            message = "An error occurred while fetching all students."

    # Close the connection
    if conn:
        conn.close()

    # Render the template
    return render_template('find_people.html',
                           student=student_info,
                           all_students=all_students,
                           message=message)


@app.route('/research-confirmation')
def research_confirmation():
    # You can pass more context to the template if needed
    return render_template('research_confirmation.html')
@app.route('/join-research', methods=['GET', 'POST'])
def join_research():
    conn = connect_to_database()
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        student_email = request.form.get('student_email')  # This will be used to find the student_id
        research_id = request.form.get('research')

        if conn:
            try:
                with conn.cursor() as cursor:
                    # Retrieve student_id using student_email
                    cursor.execute("SELECT student_id FROM students WHERE email = %s", (student_email,))
                    student_id_result = cursor.fetchone()
                    if student_id_result:
                        student_id = student_id_result[0]
                    else:
                        return render_template('error.html', message="No student found with the provided email.")

                    # Retrieve professor_id and professor_name using research_id
                    cursor.execute("""
                        SELECT p.professor_id, p.name
                        FROM research_and_projects rp
                        JOIN professors p ON rp.professor_id = p.professor_id
                        WHERE rp.project_id = %s
                    """, (research_id,))
                    research_result = cursor.fetchone()
                    if research_result:
                        professor_id, professor_name = research_result
                    else:
                        return render_template('error.html', message="No research found with the provided ID.")

                    # Retrieve research_topic using research_id
                    cursor.execute("SELECT title FROM research_and_projects WHERE project_id = %s", (research_id,))
                    research_topic_result = cursor.fetchone()
                    if research_topic_result:
                        research_topic = research_topic_result[0]
                    else:
                        return render_template('error.html', message="No research topic found with the provided ID.")

                    # Insert the new record into research_with_professors
                    cursor.execute("""
                        INSERT INTO research_with_professors (student_id, student_name, professor_id, professor_name, research_id, research_topic)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (student_id, student_name, professor_id, professor_name, research_id, research_topic))
                    conn.commit()
                return redirect(url_for('research_confirmation'))
            except psycopg2.Error as e:
                conn.rollback()
                print("Error inserting research participation data:", e)
            finally:
                conn.close()
        return render_template('error.html', message="Failed to join research.")

    # For GET request, fetch all research projects to fill the dropdown
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT project_id, title FROM research_and_projects")
                research_and_projects = cursor.fetchall()
            return render_template('join_research.html', research_and_projects=research_and_projects)
        except psycopg2.Error as e:
            print("Error fetching research projects:", e)
        finally:
            conn.close()
    return render_template('error.html', message="Unable to fetch research topics.")


@app.route('/schedule_exam', methods=['GET', 'POST'])
def schedule_exam():
    if request.method == 'POST':
        # Get form data
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        course_id = request.form.get('course_id')
        room_id = request.form.get('room_id')
        
        # Check if end time is after start time
        if end_time <= start_time:
            return "End time must be after start time."
        
        # Check if exam date is not in the past
        if datetime.strptime(date, '%Y-%m-%d').date() < datetime.now().date():
            return "Exam date cannot be in the past."

        conn = connect_to_database()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Check for time conflict
                    cursor.execute("""
                        SELECT * FROM Final_Exam_Schedule
                        WHERE room_id = %s AND date = %s AND NOT (%s >= end_time OR %s <= start_time)
                    """, (room_id, date, end_time, start_time))
                    
                    if cursor.fetchone():
                        # Conflict found
                        return "Time conflict! Please choose a different room or time."

                    # No conflict, insert exam schedule into database
                    cursor.execute("""
                        INSERT INTO Final_Exam_Schedule (date, start_time, end_time, course_id, room_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (date, start_time, end_time, course_id, room_id))
                    conn.commit()

                # Registration successful
                return "You have successfully booked your spot!"
            except psycopg2.Error as e:
                print("Database error:", e)
                return "Database error occurred."
            finally:
                conn.close()
        else:
            return "Failed to connect to database."
    else:
        # Render the form for GET requests
        return render_template('schedule_exam.html')

@app.route('/clubs')
def clubs():
    conn = connect_to_database()  # Ensure this function correctly sets up your DB connection
    if conn:
        try:
            cursor = conn.cursor()
            # Query to fetch club names and count of students in each club
            cursor.execute("""
                SELECT clubs.name, COUNT(students.club_id) as student_count
                FROM clubs
                LEFT JOIN students ON clubs.club_id = students.club_id
                GROUP BY clubs.name, clubs.club_id
                ORDER BY clubs.name;
            """)
            clubs = cursor.fetchall()  # Fetch all results
            cursor.close()
            return render_template('clubs.html', student_enrolled_club=clubs)
        except psycopg2.Error as e:
            print("Database error:", e)
            return "A database error occurred."
        finally:
            conn.close()
    else:
        return "Failed to connect to the database."


@app.route('/contact')
def contact():
    image_url = url_for('static', filename='AUB_people.jpg')
    return render_template('contact_us.html', image_url=image_url)


@app.route('/professors')
def professors():
    # Fetch all professors from the database
    professors_data = fetch_all_professors()

    # Render the template with the list of professors
    return render_template('professors.html', professors=professors_data)


@app.route('/search-professor', methods=['GET'])
def search_professor():
    professor_id = request.args.get('id')
    if professor_id:
        professor_details = fetch_professor_details(professor_id)
        return jsonify(professor_details)
    return jsonify({"error": "Professor ID not provided"}), 400


def fetch_all_professors():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Professors")
            professors_data = cursor.fetchall()
            cursor.close()
            return professors_data
        except psycopg2.Error as e:
            print("Error fetching professors data:", e)
        finally:
            conn.close()
    return []

import psycopg2
import psycopg2.extras


@app.route('/professor-details')
def professor_details():
    professor_id = request.args.get('id')
    if professor_id:
        details = fetch_professor_details(professor_id)
        # Assuming you have a template called 'professor_details.html'
        return render_template('professor_details.html', details=details)
    else:
        return "Professor ID is required.", 400


def fetch_professor_details(professor_id):
    conn = connect_to_database()
    details = {}
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT p.name, p.email, d.name AS department_name 
                FROM professors p
                LEFT JOIN departments d ON p.department_id = d.department_id 
                WHERE p.professor_id = %s
            """, (professor_id,))  # Correct parameter passing
            result = cursor.fetchone()

            if result:
                details = {
                    'name': result['name'],
                    'email': result['email'],
                    'department': result.get('department_name', 'No Department'),  # Use .get for safer access
                    'students_advised_count': 0,  # Initialize with zero
                    'students_names': [],
                    'clubs_advised': [],
                    'courses_taught': []
                }

                # Update the SQL query to correctly handle multiple aggregates in a single query
                cursor.execute("""
                    SELECT 
                        COUNT(*) AS student_count,
                        ARRAY_AGG(DISTINCT Students.Name) FILTER (WHERE Students.Name IS NOT NULL) AS student_names,
                        ARRAY_AGG(DISTINCT Clubs.Name) FILTER (WHERE Clubs.Name IS NOT NULL) AS club_names,
                        ARRAY_AGG(DISTINCT Courses.Title) FILTER (WHERE Courses.Title IS NOT NULL) AS course_titles
                    FROM Professors
                    LEFT JOIN Students ON Professors.Professor_ID = Students.Advisor_ID
                    LEFT JOIN Clubs ON Professors.Professor_ID = Clubs.Faculty_Advisor_ID
                    LEFT JOIN Courses ON Professors.Professor_ID = Courses.Professor_ID
                    WHERE Professors.Professor_ID = %s
                    GROUP BY Professors.Professor_ID
                """, (professor_id,))  # Correct parameter passing
                result = cursor.fetchone()

                if result:
                    details.update({
                        'students_advised_count': result['student_count'] or 0,
                        'students_names': result['student_names'] or [],
                        'clubs_advised': result['club_names'] or [],
                        'courses_taught': result['course_titles'] or []
                    })

            cursor.close()
            return details
        except psycopg2.Error as e:
            print("Error fetching professor details:", e)
            return {"error": "Database error"}
        finally:
            conn.close()
    else:
        return {"error": "Unable to connect to database"}



@app.route('/student_life')
def student_life():
    clubs = fetch_clubs()
    if clubs is not None:
        return render_template('student_life.html', clubs=clubs)
    else:
        return render_template('error.html', message="Error fetching clubs data")

@app.route('/student_life/register')  # Updated route
def register_club():
    clubs = fetch_clubs()  # Fetch all clubs, not just one
    return render_template('club_registration.html', clubs=clubs)

@app.route('/submit-registration', methods=['POST'])
def submit_registration():
    # Extract form data
    club_id = request.form.get('club_id')  # Assuming this is the correct form field name
    name = request.form.get('name')
    email = request.form.get('email')
    major = request.form.get('major')
    club_name = request.form.get('club')

    # Convert empty string for club_id to None
    club_id = None if club_id == '' else club_id

    # Connect to the database
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            # Insert the student into the database
            cursor.execute("""
                INSERT INTO students (name, email, major, club_id)
                VALUES (%s, %s, %s, %s)
            """, (name, email, major, club_id))  # club_id can be None which is acceptable for NULL in SQL

            conn.commit()  # Commit the transaction
            cursor.close()

            # After saving to the database, render the confirmation page with the user's name and club name
            return render_template('confirmation_club.html', name=name, club_name=club_name)

        except psycopg2.Error as e:
            conn.rollback()  # Rollback in case of error
            print("Database error:", e)
            return render_template('error.html', message="An error occurred during registration.")

        finally:
            conn.close()
    else:
        return render_template('error.html', message="Unable to connect to database")



def add_club_id_column():
    conn = connect_to_database()  # Assuming you have this function set up
    if conn:
        try:
            cursor = conn.cursor()
            # Add the club_id column
            cursor.execute("""
                ALTER TABLE students
                ADD COLUMN club_id INTEGER;
            """)
            # Add foreign key constraint
            cursor.execute("""
                ALTER TABLE students
                ADD CONSTRAINT fk_club
                FOREIGN KEY (club_id) REFERENCES clubs(club_id);
            """)
            conn.commit()
            cursor.close()
            return "Column and constraint added successfully."
        except psycopg2.Error as e:
            conn.rollback()
            return f"An error occurred: {e}"
        finally:
            conn.close()
    else:
        return "Failed to connect to the database."

def fetch_clubs():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT Clubs.Club_ID as club_id, Clubs.Name AS club_name, Professors.Name AS advisor_name
                FROM Clubs
                LEFT JOIN Professors ON Clubs.Faculty_Advisor_ID = Professors.Professor_ID
                ORDER BY Clubs.Name;
            """)
            clubs_data = cursor.fetchall()
            cursor.close()
            return clubs_data
        except psycopg2.Error as e:
            print("Error fetching clubs data:", e)
        finally:
            conn.close()
    return None





@app.route('/new-student')
def new_student():
    departments = fetch_departments()
    professors = fetch_all_professors()
    return render_template('student_registration.html', departments=departments, professors=professors)


@app.route('/register-student', methods=['POST'])
def register_student():
    name = request.form.get('name')
    email = request.form.get('email')
    major = request.form.get('major')
    department_id = request.form.get('department')
    advisor_id = request.form.get('advisor')

    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Students (Name, Email, Major, Department_ID, Advisor_ID) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, email, major, department_id, advisor_id))
                conn.commit()
            return render_template('student_registration_confirmation.html')
        except psycopg2.Error as e:
            print("Error registering student:", e)
            return render_template('error.html', message="An error occurred while registering the student.")
        finally:
            conn.close()
    else:
        return render_template('error.html', message="Unable to connect to the database.")

def fetch_all_students():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Students")
            students_data = cursor.fetchall()
            cursor.close()
            return students_data
        except psycopg2.Error as e:
            print("Error fetching students data:", e)
        finally:
            conn.close()
    return []

from flask import render_template

@app.route('/hire-professor', methods=['GET'])
def hire_professor_form():
    departments = fetch_departments()
    students = fetch_all_students()  # Fetch all existing students
    return render_template('hire_professor.html', departments=departments, students=students)

@app.route('/hire-professor', methods=['POST'])
def hire_professor():
    # Extract form data
    name = request.form.get('name')
    email = request.form.get('email')
    department_id = request.form.get('department')
    selected_students = request.form.getlist('students')

    # Insert new professor into the database
    professor_id = insert_new_professor(name, email, department_id)

    # If any students were selected, update their advisor to the new professor
    if selected_students:
        update_students_advisor(selected_students, professor_id)

    # Redirect to a confirmation page or wherever you'd like
    return redirect(url_for('home'))

def fetch_research_data():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM research_with_professors")
            research_data = cursor.fetchall()
            cursor.close()
            conn.close()
            return research_data
        except psycopg2.Error as e:
            print("Error fetching research data:", e)
    return None

def insert_new_professor(name, email, department_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Professors (Name, Email, Department_ID) 
                    VALUES (%s, %s, %s) RETURNING Professor_ID;
                """, (name, email, department_id))
                professor_id = cursor.fetchone()[0]
                conn.commit()
                return professor_id
        except psycopg2.Error as e:
            print("Error inserting new professor:", e)
            return None
        finally:
            conn.close()
    return None
def update_students_advisor(student_ids, professor_id):
    conn = connect_to_database()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Update each student's advisor to the new professor's ID
                for student_id in student_ids:
                    cursor.execute("""
                        UPDATE Students SET Advisor_ID = %s WHERE Student_ID = %s;
                    """, (professor_id, student_id))
                conn.commit()
        except psycopg2.Error as e:
            print("Error updating students' advisor:", e)
        finally:
            conn.close()
            
            
openai.api_key="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"


@app.route('/chatbot_response', methods=['POST'])
def chatbot_response():
    data = request.json
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Your system message here if any"},
                      {"role": "user", "content": data['message']}]
        )
        # Depending on the version you might need to adjust how you access the response
        res = response['choices'][0]['message']['content']
        return jsonify({'response': res})
    except Exception as e:
        # Log the error and return a 500 server error response to the client
        print(e)
        return jsonify({'error': 'An error occurred while processing your request.'}), 500
    

if __name__ == "__main__":
    app.run(debug=True)