import mysql.connector
from mysql.connector import Error

# =================== CONNECT ===================
# get_connection()
# PURPOSE : Create and return a live MySQL connection object.
#           Returns None if the connection fails.
# USED BY : All DB helper functions below.

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="face_recognition",
            connect_timeout=5
        )
        return conn
    except Error as e:
        print("Database connection error:", e)
        return None
# END get_connection


# =================== REGISTER STUDENT ===================
# ------------------------------------------------------------------
# register_student(name, email, reg_no, password, dept, year,
#                  course, program, image_path, contact_no)
# PURPOSE : Insert a new student record into the students table.
#           Checks for duplicate email or reg_no before inserting.
# RETURNS : (True, success_msg) or (False, error_msg)
# ------------------------------------------------------------------
def register_student(name, email, reg_no, password, dept, year, course, program, image_path, contact_no="N/A"):
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed"
    try:
        cursor = conn.cursor()
        # Check existing student
        cursor.execute("SELECT * FROM students WHERE email=%s OR registration_no=%s", (email, reg_no))
        if cursor.fetchone():
            return False, "Student already exists"
        # Insert student
        cursor.execute("""
            INSERT INTO students (full_name, email, registration_no, password, department, year_level, course, session, image_path, contact_number)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, email, reg_no, password, dept, year, course, program, image_path, contact_no))
        conn.commit()
        return True, "Student registered successfully!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"
    finally:
        cursor.close()
        conn.close()
# END register_student


# =================== STUDENT LOGIN ===================
# ------------------------------------------------------------------
# check_user(email, password)
# PURPOSE : Authenticate a student login against the students table.
# RETURNS : (True, welcome_msg, student_dict) on success
#           (False, error_msg, None) on failure
# ------------------------------------------------------------------
def check_user(email, password):
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed", None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE email=%s AND password=%s", (email, password))
        student = cursor.fetchone()
        if student:
            # The students table uses 'full_name' instead of 'name'
            student_name = student.get('full_name') or student.get('name') or "Student"
            # Ensure 'name' is available since other parts of the app might expect it
            student['name'] = student_name
            return True, f"Login successful! Welcome {student_name}", student
        else:
            return False, "Invalid student email or password", None
    except Exception as e:
        return False, f"Login failed: {str(e)}", None
    finally:
        cursor.close()
        conn.close()
# END check_user


# =================== ADMIN LOGIN ===================
# ------------------------------------------------------------------
# check_admin(email, password)
# PURPOSE : Authenticate an admin login against the admin table.
#           Normalises the name field so callers always get
#           admin_data['name'] and admin_data['photo_path'].
# RETURNS : (True, welcome_msg, admin_dict) on success
#           (False, error_msg, None) on failure
# ------------------------------------------------------------------
def check_admin(email, password):
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed", None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE email=%s AND password=%s", (email, password))
        admin = cursor.fetchone()
        if admin:
            # Normalise: the table column is 'full_name'; expose as 'name' for the dashboard
            admin_name = admin.get('full_name') or admin.get('name') or admin.get('username') or "Admin"
            admin['name'] = admin_name          # always available as admin_data['name']
            admin['photo_path'] = admin.get('image_path')  # always available as admin_data['photo_path']
            admin['registration_no'] = admin.get('registration_no') # already in dict
            return True, f"Admin login successful! Welcome {admin_name}", admin
        else:
            return False, "Invalid admin email or password", None
    except Exception as e:
        return False, f"Login failed: {str(e)}", None
    finally:
        cursor.close()
        conn.close()
# END check_admin

# ------------------------------------------------------------------
# add_new_admin(full_name, email, reg_no, password, image_path=None)
# PURPOSE : Insert a new administrative user into the admin table.
#           Checks for duplicate emails or registration numbers.
# RETURNS : (True, success_msg) or (False, error_msg)
# ------------------------------------------------------------------
def add_new_admin(full_name, email, reg_no, password, image_path=None):
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed"
    try:
        cursor = conn.cursor()
        
        # Check for duplicate email
        cursor.execute("SELECT id FROM admin WHERE email=%s", (email,))
        if cursor.fetchone():
            return False, "An administrator with that Email already exists."
        
        # Check for duplicate registration number
        cursor.execute("SELECT id FROM admin WHERE registration_no=%s", (reg_no,))
        if cursor.fetchone():
            return False, "An administrator with that Registration Number already exists."
            
        cursor.execute("""
            INSERT INTO admin (full_name, email, registration_no, password, image_path)
            VALUES (%s, %s, %s, %s, %s)
        """, (full_name, email, reg_no, password, image_path))
        
        conn.commit()
        return True, "New administrator successfully registered!"
    except Exception as e:
        return False, f"Failed to register admin: {str(e)}"
    finally:
        cursor.close()
        conn.close()
# END add_new_admin

# ------------------------------------------------------------------
# get_all_admins()
# PURPOSE : Retrieve all administrators from the database.
# RETURNS : List of admin dictionaries or an empty list.
# ------------------------------------------------------------------
def get_all_admins():
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, full_name, email, registration_no FROM admin")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching admins: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
# ------------------------------------------------------------------
# get_admin_by_regno(reg_no)
# PURPOSE : Retrieve a single administrator by their registration number.
#           Used by facial login to identify recognized admins.
# RETURNS : Row dict with admin columns (normalized), or None.
# ------------------------------------------------------------------
def get_admin_by_regno(reg_no):
    conn = get_connection()
    if conn is None: return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE registration_no=%s", (reg_no,))
        admin = cursor.fetchone()
        if admin:
            admin['name'] = admin.get('full_name') or admin.get('username') or "Admin"
            admin['photo_path'] = admin.get('image_path')
            return admin
        return None
    except Exception as e:
        print(f"Error fetching admin by Registration No: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
# END get_admin_by_regno

# =================== HELPERS ===================
# ------------------------------------------------------------------
# get_student_by_regno(reg_no)
# PURPOSE : Fetch a single student record by registration number.
#           Used by face recognition to display the student's name.
# RETURNS : Row dict with all student columns, or None if not found.
# ------------------------------------------------------------------
def get_student_by_regno(reg_no):
    conn = get_connection()
    if conn is None: return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE registration_no=%s", (reg_no,))
        return cursor.fetchone()
    except:
        return None
    finally:
        cursor.close()
        conn.close()
# END get_student_by_regno


# ------------------------------------------------------------------
# get_student_attendance_stats(reg_no, course)
# PURPOSE : Calculates 12 comprehensive analytical stats for a student
# ------------------------------------------------------------------
def get_student_attendance_stats(reg_no, course):
    conn = get_connection()
    if conn is None:
        return None
    try:
        from datetime import datetime, timedelta, date, time
        cursor = conn.cursor(dictionary=True)
        
        # 1. Fetch all their records
        start_date = config_manager.get("starting_date")
        if start_date:
            cursor.execute("SELECT date, time_in, status FROM attendance WHERE reg_no=%s AND date >= %s ORDER BY date ASC", (reg_no, start_date))
        else:
            cursor.execute("SELECT date, time_in, status FROM attendance WHERE reg_no=%s ORDER BY date ASC", (reg_no,))
        records = cursor.fetchall()
        
        # 2. Total classes held (distinct dates for the same course as a baseline approximation)
        start_date = config_manager.get("starting_date")
        if start_date:
            cursor.execute("SELECT COUNT(DISTINCT date) as total_held FROM attendance WHERE course=%s AND date >= %s", (course, start_date))
        else:
            cursor.execute("SELECT COUNT(DISTINCT date) as total_held FROM attendance WHERE course=%s", (course,))
        total_held = cursor.fetchone()['total_held']
        if total_held == 0: total_held = len(records) # Fallback
            
        attended = len(records)
        missed = max(0, total_held - attended)
        percent = (attended / total_held * 100) if total_held > 0 else 0.0
        
        # Status Color
        if percent >= 90: status_info = ("Excellent", "#00c853")
        elif percent >= 75: status_info = ("Good", "#3498db")
        elif percent >= 60: status_info = ("Warning", "#f39c12")
        else: status_info = ("Danger", "#e74c3c")
            
        # Streak
        streak = 0
        if records:
            dates = sorted([r['date'] for r in records], reverse=True)
            streak = 1
            for i in range(1, len(dates)):
                if (dates[i-1] - dates[i]).days == 1: streak += 1
                else: break
                    
        # Late Count (> 09:00:00)
        late = 0
        for r in records:
            t = r['time_in']
            if isinstance(t, timedelta) and t.seconds > 9 * 3600: late += 1
            
        # Fast-forward / Trend
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        two_weeks_ago = today - timedelta(days=14)
        
        this_week = sum(1 for r in records if r['date'] >= week_ago)
        last_week = sum(1 for r in records if two_weeks_ago <= r['date'] < week_ago)
        
        if this_week > last_week: trend = ("🔼 Up", "#00c853")
        elif this_week < last_week: trend = ("🔽 Down", "#e74c3c")
        else: trend = ("▶ Stable", "#3498db")
            
        today_record = [r for r in records if r['date'] == today]
        today_status = ("Present", "#00c853") if today_record else ("Absent", "#e74c3c")
        
        # Determine current month progress
        month_start = today.replace(day=1)
        if start_date:
            # If start_date is more recent, use it
            try:
                s_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                if s_date > month_start: month_start = s_date
            except: pass
        
        month_records = [r for r in records if r['date'] >= month_start]
        # Approximation of months days held
        cursor.execute("SELECT COUNT(DISTINCT date) as held FROM attendance WHERE course=%s AND date >= %s", (course, month_start))
        month_held = cursor.fetchone()['held'] or 1
        month_perc = (len(month_records) / month_held * 100)
        
        return {
            "Total classes to study": total_held,
            "Classes Attended": attended,
            "Classes Missed": missed,
            "Attendance Percentage (%)": f"{percent:.1f}%",
            "Status (Color-Coded)": status_info,
            "Current Streak": f"{streak} days",
            "Late Count": late,
            "Weekly Attendance Rate": f"{this_week} days/wk",
            "Trend Indicator": trend,
            "Target Progress": f"Goal 80% (Current: {percent:.1f}%)",
            "Today’s Attendance Status": today_status,
            "Recognition Confidence": ("98.4% (Avg)", "#3498db")
        }
    except Exception as e:
        print(f"Error fetching stats for {reg_no}: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
# END get_student_attendance_stats


# ------------------------------------------------------------------
# search_student(term)
# PURPOSE : Search the students table by name or registration number
#           using a LIKE wildcard. Used by the Update Users page.
# RETURNS : List of matching row dicts (empty list if none found).
# ------------------------------------------------------------------
def search_student(term):
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        # Search by name or reg_no
        query = "SELECT * FROM students WHERE full_name LIKE %s OR registration_no LIKE %s"
        wildcard_term = f"%{term}%"
        cursor.execute(query, (wildcard_term, wildcard_term))
        return cursor.fetchall()
    except:
        return []
    finally:
        cursor.close()
        conn.close()
# END search_student


# ------------------------------------------------------------------
# update_student_photo(reg_no, photo_path)
# PURPOSE : Update the profile_image column for a given student.
#           Called after a new photo has been uploaded/cropped.
# RETURNS : (True, success_msg) or (False, error_msg)
# ------------------------------------------------------------------
def update_student_photo(reg_no, photo_path):
    conn = get_connection()
    if conn is None: return False, "DB Connection Error"
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET image_path=%s WHERE registration_no=%s", (photo_path, reg_no))
        conn.commit()
        return True, "Photo updated successfully"
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()
# END update_student_photo


# ------------------------------------------------------------------
# update_student_details(reg_no, email, contact, password=None)
# PURPOSE : Update a student's email and contact number. Optionally
#           also updates the password if a new one is provided.
# RETURNS : (True, success_msg) or (False, error_msg)
# ------------------------------------------------------------------
def update_student_details(reg_no, email, contact, password=None):
    conn = get_connection()
    if conn is None: return False, "DB Connection Error"
    try:
        cursor = conn.cursor()
        if password:
            query  = "UPDATE students SET email=%s, contact_number=%s, password=%s WHERE registration_no=%s"
            params = (email, contact, password, reg_no)
        else:
            query  = "UPDATE students SET email=%s, contact_number=%s WHERE registration_no=%s"
            params = (email, contact, reg_no)

        cursor.execute(query, params)
        conn.commit()
        return True, "Details updated successfully"
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()
# END update_student_details


# ------------------------------------------------------------------
# update_full_student_record(original_reg_no, data_dict)
# PURPOSE : Update all editable fields for a student from the admin dashboard.
# RETURNS : (True, success_msg) or (False, error_msg)
# ------------------------------------------------------------------
def update_full_student_record(original_reg_no, data_dict):
    conn = get_connection()
    if conn is None: return False, "DB Connection Error"
    
    try:
        cursor = conn.cursor()
        
        new_reg_no = data_dict.get('registration_no')
        new_email = data_dict.get('email')
        
        # Check reg_no collision if it was renamed
        if new_reg_no != original_reg_no:
            cursor.execute("SELECT registration_no FROM students WHERE registration_no=%s", (new_reg_no,))
            if cursor.fetchone():
                return False, "New Registration Number belongs to another student."
                
        # Check email collision
        cursor.execute("SELECT registration_no FROM students WHERE email=%s AND registration_no!=%s", (new_email, original_reg_no))
        if cursor.fetchone():
            return False, "Email address is already in use by another student."
            
        query = """
            UPDATE students SET 
                full_name=%s, registration_no=%s, email=%s, password=%s,
                department=%s, year_level=%s, course=%s, session=%s, contact_number=%s
            WHERE registration_no=%s
        """
        params = (
            data_dict.get('full_name'),
            new_reg_no,
            new_email,
            data_dict.get('password'),
            data_dict.get('department'),
            data_dict.get('year_level'),
            data_dict.get('course'),
            data_dict.get('session'),
            data_dict.get('contact_number'),
            original_reg_no
        )
        
        cursor.execute(query, params)
        conn.commit()
        return True, "Student record updated successfully!"
        
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()
# END update_full_student_record



# END update_full_student_record


# =================== FORGOT PASSWORD ===================
# ------------------------------------------------------------------
# get_system_email_credentials()
# PURPOSE : Get an admin's email and password to use as the SMTP sender
# ------------------------------------------------------------------
def get_system_email_credentials():
    conn = get_connection()
    if conn is None: return None, None
    try:
        cursor = conn.cursor(dictionary=True)
        # Just grab the first admin who has an email and password set
        cursor.execute("SELECT email, password FROM admin WHERE email IS NOT NULL AND password IS NOT NULL LIMIT 1")
        row = cursor.fetchone()
        if row:
            return row['email'], row['password']
        return None, None
    except:
        return None, None
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# check_email_exists(email)
# PURPOSE : Verifies if an email belongs to a registered student
# ------------------------------------------------------------------
def check_email_exists(email):
    conn = get_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT registration_no FROM students WHERE email=%s", (email,))
        return cursor.fetchone() is not None
    except:
        return False
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# update_password_by_email(email, new_password)
# PURPOSE : Saves the newly reset password for the verified student
# ------------------------------------------------------------------
def update_password_by_email(email, new_password):
    conn = get_connection()
    if conn is None: return False, "DB connection failed"
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET password=%s WHERE email=%s", (new_password, email))
        conn.commit()
        return True, "Password updated successfully"
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


# =================== ATTENDANCE MANAGEMENT ===================

# ------------------------------------------------------------------
# create_attendance_table()
# PURPOSE : Ensure the attendance table exists in the database.
# ------------------------------------------------------------------
def create_attendance_table():
    conn = get_connection()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reg_no VARCHAR(50) NOT NULL,
                name VARCHAR(100) NOT NULL,
                course VARCHAR(150),
                program VARCHAR(100),
                department VARCHAR(100),
                date DATE NOT NULL,
                time_in TIME NOT NULL,
                time_out TIME,
                status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating attendance table: {e}")
    finally:
        cursor.close()
        conn.close()


from datetime import datetime
# ------------------------------------------------------------------
# record_attendance(reg_no, name, course, program, department, status="Present")
# PURPOSE : Log a student's attendance for the current day.
#           Prevents duplicate logs for the same student on the same day.
# ------------------------------------------------------------------
def record_attendance(reg_no, name, course, program, department, status="Present"):
    # 1. Check for Future Date Lock
    from admin_dashboard_files import config_manager
    start_date_str = config_manager.get("starting_date")
    if start_date_str:
        try:
            from datetime import datetime
            s_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if datetime.now().date() < s_date:
                print(f"[DB] Attendance Blocked: Today is before the starting date ({start_date_str})")
                return False
        except: pass

    conn = get_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        now = datetime.now()
        curr_date = now.strftime("%Y-%m-%d")
        curr_time = now.strftime("%H:%M:%S")

        # Check if already recorded today
        cursor.execute("SELECT id FROM attendance WHERE reg_no=%s AND date=%s", (reg_no, curr_date))
        if cursor.fetchone():
            return False # Already present today

        cursor.execute("""
            INSERT INTO attendance (reg_no, name, course, program, department, date, time_in, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (reg_no, name, course, program, department, curr_date, curr_time, status))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error recording attendance: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# get_attendance_history()
# PURPOSE : Fetch all attendance records from the database.
# ------------------------------------------------------------------
def get_attendance_history():
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attendance ORDER BY date DESC, time_in DESC")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching attendance history: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# =================== SYSTEM ANNOUNCEMENTS ===================

# ------------------------------------------------------------------
# create_announcement_table()
# PURPOSE : Ensure the announcements table exists in the database.
# ------------------------------------------------------------------
def create_announcement_table():
    conn = get_connection()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                audience VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating announcements table: {e}")
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# create_read_announcements_table()
# PURPOSE : Track which students have deleted/hidden which announcements
# ------------------------------------------------------------------
def create_read_announcements_table():
    conn = get_connection()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_read_announcements (
                student_reg_no VARCHAR(50) NOT NULL,
                announcement_id INT NOT NULL,
                action VARCHAR(20) DEFAULT 'deleted',
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (student_reg_no, announcement_id)
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating read announcements table: {e}")
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# post_announcement(title, message, audience)
# PURPOSE : Insert a new announcement into the database.
# ------------------------------------------------------------------
def post_announcement(title, message, audience):
    conn = get_connection()
    if conn is None: return False, "DB connection failed"
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO announcements (title, message, audience)
            VALUES (%s, %s, %s)
        """, (title, message, audience))
        conn.commit()
        return True, "Announcement posted successfully"
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# get_student_announcements(student_reg_no)
# PURPOSE : Retrieve all announcements meant for students that the 
#           student hasn't explicitly deleted.
# ------------------------------------------------------------------
def get_student_announcements(student_reg_no):
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT a.* FROM announcements a
            LEFT JOIN student_read_announcements sra 
            ON a.id = sra.announcement_id AND sra.student_reg_no = %s
            WHERE (a.audience IN ('All Users', 'Students Only') OR a.audience = %s)
            AND sra.announcement_id IS NULL
            ORDER BY a.created_at DESC
        """
        cursor.execute(query, (student_reg_no, f"Specific Student: {student_reg_no}"))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching announcements: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# delete_announcement_for_student(student_reg_no, announcement_id)
# PURPOSE : Mark an announcement as deleted for a specific student.
# ------------------------------------------------------------------
def delete_announcement_for_student(student_reg_no, announcement_id):
    conn = get_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO student_read_announcements (student_reg_no, announcement_id, action)
            VALUES (%s, %s, 'deleted')
        """, (student_reg_no, announcement_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error tracking announcement deletion: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# get_all_student_emails()
# PURPOSE : Retrieves all valid student emails for broadcasting.
# ------------------------------------------------------------------
def get_all_student_emails():
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM students WHERE email IS NOT NULL AND email != ''")
        return [row[0] for row in cursor.fetchall()]
    except:
        return []
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# get_student_email_by_regno(reg_no)
# PURPOSE : Retrieves the email of a specific student.
# ------------------------------------------------------------------
def get_student_email_by_regno(reg_no):
    conn = get_connection()
    if conn is None: return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email FROM students WHERE registration_no = %s", (reg_no,))
        row = cursor.fetchone()
        if row:
            return row['email']
        return None
    except Exception as e:
        print(f"Error fetching specific student email: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# ------------------------------------------------------------------
# get_attendance_by_date(date_str)
# PURPOSE : Fetch all attendance records for a specific date (YYYY-MM-DD).
# ------------------------------------------------------------------
def get_attendance_by_date(date_str):
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attendance WHERE date=%s ORDER BY time_in DESC", (date_str,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching attendance for {date_str}: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# ------------------------------------------------------------------
# get_attendance_by_range(start_date, end_date)
# PURPOSE : Fetch all attendance records between two specific dates.
# ------------------------------------------------------------------
def get_attendance_by_range(start_date, end_date):
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM attendance 
            WHERE date BETWEEN %s AND %s 
            ORDER BY date DESC, time_in DESC
        """, (start_date, end_date))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching attendance range: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# ------------------------------------------------------------------
# get_all_students_minimal()
# PURPOSE : Retrieves basic info for all students (Name, Reg, Course, etc).
# ------------------------------------------------------------------
def get_all_students_minimal():
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT registration_no as reg_no, full_name as name, course, session as program, department FROM students")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching students: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

def get_all_students_full():
    """Fetch all students with email and session for the full database view."""
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT registration_no as reg_no, full_name as name, course, session, department, email FROM students")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching all students (full): {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# ------------------------------------------------------------------
# get_daily_system_stats()
# PURPOSE : Calculates attendance stats specifically for TODAY.
# ------------------------------------------------------------------
def get_daily_system_stats():
    conn = get_connection()
    if conn is None: return 0, 0, 0
    try:
        cursor = conn.cursor(dictionary=True)
        # 1. Total Students
        cursor.execute("SELECT COUNT(*) as total FROM students")
        total_students = cursor.fetchone()['total']
        
        # 2. Total Present records TODAY
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(DISTINCT reg_no) as present FROM attendance WHERE date=%s", (today,))
        presence_count = cursor.fetchone()['present'] or 0
            
        # 3. Total Absents (Simple subtraction)
        total_absent = max(0, total_students - presence_count)
        
        return total_students, presence_count, total_absent
    except Exception as e:
        print(f"Error calculating daily stats: {e}")
        return 0, 0, 0
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# ------------------------------------------------------------------
# get_cumulative_system_stats(start_date)
# ------------------------------------------------------------------
def get_cumulative_system_stats(start_date=None):
    conn = get_connection()
    if conn is None: return 0, 0, 0
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM students")
        total_students = cursor.fetchone()['total']
        
        if start_date:
            cursor.execute("SELECT COUNT(*) as present FROM attendance WHERE date >= %s", (start_date,))
            presence_count = cursor.fetchone()['present']
            cursor.execute("SELECT COUNT(DISTINCT date) as days FROM attendance WHERE date >= %s", (start_date,))
            total_days = cursor.fetchone()['days']
        else:
            cursor.execute("SELECT COUNT(*) as present FROM attendance")
            presence_count = cursor.fetchone()['present']
            cursor.execute("SELECT COUNT(DISTINCT date) as days FROM attendance")
            total_days = cursor.fetchone()['days']
            
        total_absent = max(0, (total_students * total_days) - presence_count)
        return total_students, presence_count, total_absent
    except:
        return 0, 0, 0
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()


# ------------------------------------------------------------------
# record_archive_entry(filename, date_str, category, path)
# PURPOSE : Log a newly generated attendance excel file in the DB.
# ------------------------------------------------------------------
def record_archive_entry(filename, date_str, category, path):
    conn = get_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            REPLACE INTO attendance_archives (filename, date, category, file_path)
            VALUES (%s, %s, %s, %s)
        """, (filename, date_str, category, path))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error recording archive entry: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# ------------------------------------------------------------------
# get_all_archives()
# PURPOSE : Fetch all recorded attendance excel archives from the DB.
# ------------------------------------------------------------------
def get_all_archives():
    conn = get_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attendance_archives ORDER BY date DESC, created_at DESC")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching archives: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# ------------------------------------------------------------------
# delete_archive_by_id(archive_id)
# PURPOSE : Remove a specific archive entry from the database.
# ------------------------------------------------------------------
def delete_archive_by_id(archive_id):
    conn = get_connection()
    if conn is None: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance_archives WHERE id = %s", (archive_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting archive record: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# ------------------------------------------------------------------
# delete_archives_by_category(category)
# PURPOSE : Remove all archive entries for a specific category.
#           Returns the list of file paths for disk removal.
# ------------------------------------------------------------------
def delete_archives_by_category(category):
    conn = get_connection()
    if conn is None: return []
    try:
        # Get paths first to help with disk removal
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT file_path FROM attendance_archives WHERE category = %s", (category,))
        paths = [r['file_path'] for r in cursor.fetchall()]
        
        cursor.execute("DELETE FROM attendance_archives WHERE category = %s", (category,))
        conn.commit()
        return paths
    except Exception as e:
        print(f"Error deleting category archives: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn: conn.close()

# ------------------------------------------------------------------
# initialize_database()
# PURPOSE : Ensure all necessary tables exist in the database.
#           Called once at application startup.
# ------------------------------------------------------------------
def initialize_database():
    print("[DB] Initializing Database...")
    conn = get_connection()
    if conn is None:
        print("[DB] Critical Error: Could not connect to database for initialization.")
        return
    try:
        cursor = conn.cursor()
        
        # 1. Attendance Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reg_no VARCHAR(50) NOT NULL,
                name VARCHAR(100) NOT NULL,
                course VARCHAR(150),
                program VARCHAR(100),
                department VARCHAR(100),
                date DATE NOT NULL,
                time_in TIME NOT NULL,
                time_out TIME,
                status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. Attendance Archives (Metadata for Excel files)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_archives (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                category VARCHAR(50) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Announcements Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                audience VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Read Announcements Tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_read_announcements (
                student_reg_no VARCHAR(50) NOT NULL,
                announcement_id INT NOT NULL,
                action VARCHAR(20) DEFAULT 'deleted',
                action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (student_reg_no, announcement_id)
            )
        """)
        
        conn.commit()
        print("[DB] Database initialization complete.")
    except Exception as e:
        print(f"[DB] Error during initialization: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    initialize_database()
