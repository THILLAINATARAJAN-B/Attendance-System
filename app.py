from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from PIL import Image
import qrcode
import io
import base64
import psycopg2
import secrets
import bcrypt
import uuid
import datetime
from pyzbar.pyzbar import decode
from io import BytesIO
import os

secret_key = secrets.token_hex(32)

app = Flask(__name__)
app.secret_key = secret_key

dbhost = 'localhost'
dbname = 'Attendance'
dbuser = 'postgres'
dbpass = '1234'

def generate_user_id():
    return str(uuid.uuid4())

def get_db_connection():
    try:
        conn = psycopg2.connect(host=dbhost, dbname=dbname, user=dbuser, password=dbpass)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def check_user(email, password, user_type):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if user_type == 'staff':
                cur.execute("SELECT password FROM staffs WHERE email = %s", (email,))
            elif user_type == 'student':
                cur.execute("SELECT password FROM students WHERE email = %s", (email,))
            result = cur.fetchone()
            if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                return True
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return False

def user_info(email, password, user_type):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            if user_type == 'staff':
                cur.execute("SELECT staff_id, user_name,type,college_id, department,language,d_o_b,email,mobile,whats_app,address,password FROM staffs WHERE email = %s", (email,))
            elif user_type == 'student':
                cur.execute("SELECT student_id, user_name,type,college_id, department_id,language,d_o_b,email,mobile,whats_app,address,password FROM students WHERE email = %s", (email,))
            result = cur.fetchone()
            if result and bcrypt.checkpw(password.encode('utf-8'), result[-1].encode('utf-8')):
                return result
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return None

def session_update(data):
    # Extract components from qr_code_data
            parts = data.split('|')
            print("parts::::::::::::::::",parts)
            # Extracting staff ID
            staff_id = parts[0]

            # Extracting class data
            class_data = parts[1]

            # Extracting college ID (first 4 characters)
            college_id = class_data[:4]

            # Extracting subject code (excluding department and semester)
            subject_code = class_data[-6:]

            # Extracting department (excluding college ID)
            department_end_index = class_data.find(str(int(class_data[-7])))  # Finding the index of the last digit (semester)
            department = class_data[4:department_end_index]

            # Extracting semester (last character)
            semester = class_data[department_end_index]


            print("Staff ID:", staff_id)
            print("College ID:", college_id)
            print("Department:", department)
            print("Semester:", semester)
            print("Subject Code:", subject_code)
            session['college_id']=college_id
            session['department']=department
            session['semester']=semester
            session['subject_code']=subject_code

def college_table():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()

            cur.execute('SELECT DISTINCT college_id FROM college')
            college_id = cur.fetchall()
                # Update the out_time for all students who haven't recorded it yet
                                # Fetch department names
            cur.execute('SELECT DISTINCT semester FROM college')
            sem = cur.fetchall()

            cur.execute('SELECT DISTINCT department FROM college')
            departments = cur.fetchall()

                # Fetch subject codes
            cur.execute('SELECT DISTINCT subject_code FROM college')
            subject_codes = cur.fetchall()

            print(college_id,departments,sem,subject_codes)
            return college_id,departments,sem,subject_codes
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

def verify_clg_dept(college, department):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()

            # Check if the given college and department exist in the database
            cur.execute('''
                SELECT *
                FROM college
                WHERE college_id = %s AND department = %s
            ''', (college, department))
            exists = cur.fetchone() is not None
            
            cur.close()
            conn.close()
            return exists
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    
@app.route("/Register", methods=['POST', 'GET'])
def register():
    college_id,departments,sem,subject_codes=college_table()
    error_message = None
    if request.method == 'POST':
        user_id = generate_user_id()
        person_name = request.form.get('person_name')
        user_type = request.form.get('type')
        college=request.form.get('college')
        department = request.form.get('department')
        d_o_b = request.form.get('d_o_b')
        language = request.form.get('language')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        whats_app = request.form.get('whats_app')
        address = request.form.get('address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                print(user_type)
                print(verify_clg_dept(college,department))
                
                if user_type == 'staff':
                    if not verify_clg_dept(college, department):
                        error_message = "Selected college or department does not exist."
                    cur.execute("SELECT COUNT(*) FROM staffs WHERE email = %s", (email,))
                elif user_type == 'student':
                    if not verify_clg_dept(college, department):
                        error_message = "Selected college or department does not exist."
                    cur.execute("SELECT COUNT(*) FROM students WHERE email = %s", (email,))
                existing_email_count = cur.fetchone()[0]
                if existing_email_count > 0:
                    error_message = 'Email already in use. Please use a different email.'
                elif len(password) < 6 or len(password) > 14:
                    error_message = 'Password must be between 6 to 14 characters.'
                elif password != confirm_password:
                    error_message = 'Passwords do not match.'
                
                else:
                    print("registering started")
                    if user_type == 'staff':
                        print("staff register started")
                        print(user_id, person_name, user_type, college, department, d_o_b, language, email, mobile, whats_app, address, hashed_password.decode('utf-8'))
                        cur.execute('''
                        INSERT INTO staffs (staff_id, user_name, type, college_id, department, d_o_b, language, email, mobile, whats_app, address, password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (user_id, person_name, user_type, college, department, d_o_b, language, email, mobile, whats_app, address, hashed_password.decode('utf-8')))
                    elif user_type == 'student':
                        print("staff register started")
                        cur.execute('''
                        INSERT INTO students (student_id, user_name, type, college_id, department_id, d_o_b, language, email, mobile, whats_app, address, password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (user_id, person_name, user_type, college, department, d_o_b, language, email, mobile, whats_app, address, hashed_password.decode('utf-8')))
                    conn.commit()
                    flash('Registration successful!', 'success')
                    return redirect(url_for('index'))  # Redirect to index after successful registration
            except psycopg2.Error as e:
                flash(f'Database error: {e}', 'danger')
            finally:
                conn.close()
    return render_template("Register.html", error_message=error_message,departments=departments, college=college_id,subject_codes=subject_codes,sem=sem)

def session_storage(data):
    session['user_id'] = data[0]
    session['user_name'] = data[1]
    session['type']=data[2]
    session['user_college']=data[3]
    session['user_department']=data[4]
    session['d_o_b'] = data[5]
    session['language'] = data[6]
    session['email'] = data[7]
    session['mobile']=data[8]
    session['whatsapp'] = data[9]
    session['address'] = data[10]

def session_getting():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    type=session.get('type')
    user_college_id=session.get('user_college')
    user_department=session.get('user_department')
    d_o_b = session.get('d_o_b')
    language = session.get('language')
    email = session.get('email')
    mobile=session.get('mobile')
    whatsapp_num = session.get('whatsapp')
    address = session.get('address')

    USER_DETAILS = [user_id, user_name,type,user_college_id, user_department, d_o_b, language, email, whatsapp_num, address]
    print("USER DETAILS=", USER_DETAILS)
    return USER_DETAILS

def user_available():
    users_data = session_getting()
    if users_data:
        return True
    return False

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('type')  # Assuming you have a form field for user type
        print("check ",email, password, user_type)  # Just for debugging purposes, remove in production

        if check_user(email, password, user_type):
            print('Login successful')
            information = user_info(email, password, user_type)
            print(information)
            session_storage(information)
            if user_type == 'staff':
                return redirect(url_for('staff'))
            elif user_type == 'student':
                return redirect(url_for('student'))

        print('Login failed. Please check your credentials.')

    # Pass QR code data to the template
    return render_template('index.html')

# Function to get the current date and time
def get_current_datetime():
    return datetime.datetime.now()

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if session.get('type')=='staff':
        staff_user_id = session.get('user_id')
        if staff_user_id:
            current_datetime = get_current_datetime()
            conn = get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    # Update the out_time for all students who haven't recorded it yet
                    cur.execute("""
                        UPDATE attendance
                        SET out_time = %s
                        WHERE staff_id = %s AND out_time IS NULL
                    """, (current_datetime, staff_user_id))

                    # Set the QR code to None for the staff member
                    cur.execute("""
                        UPDATE staffs
                        SET qr_code = NULL
                        WHERE staff_id = %s
                    """, (staff_user_id,))
                    
                    conn.commit()
                    session['qr_image_base64'] = False
                    flash('Class closed, leave time recorded for all students, and QR code deleted.','success')
                except psycopg2.Error as e:
                    print(f"Database error: {e}")
                finally:
                    conn.close()
    session.clear()
    return redirect(url_for('index'))

#========================================================================================================
                        #For Staff
#========================================================================================================

# Define route for staff home page
@app.route('/staff')
def staff():
    college_id,departments,sem,subject_codes=college_table()
    user_details = session_getting()
    qr_image_base64 = session.get('qr_image_base64', None)
    return render_template('staff.html', user_details=user_details, qr_image_base64=qr_image_base64,departments=departments, college=college_id,subject_codes=subject_codes,sem=sem)

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    college_id=request.form.get('college')
    sem=request.form.get('sem')
    department=request.form.get('Department')
    subject_code = request.form.get('subject_code')
    staff_user_id = session.get('user_id')
    print(sem,department,subject_code)
    verify_sub_code(sem,department,subject_code)
    print(staff_user_id,subject_code)
    if staff_user_id and subject_code and verify_sub_code:
        user_details = session_getting()
        # Generate QR code data combining user_id and subject code
        qr_code_data = f"{staff_user_id}|{college_id}{department}{sem}{subject_code}"
        qr_code = qrcode.make(qr_code_data)
        buffered = io.BytesIO()
        qr_code.save(buffered, format="PNG")
        qr_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        print("QR Code generated:", qr_image_base64)
        
        # Save QR code data in the database
        user_id = user_details[0]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE staffs SET qr_code = %s WHERE staff_id = %s", (qr_code_data, user_id))
        conn.commit()
        conn.close()
        
        # Save the generated QR code in the session
        session['qr_image_base64'] = qr_image_base64
        
        flash('QR code generated successfully!','success')
        return redirect(url_for('staff'))
    
    flash('Error generating QR code. Please try again.', 'danger')
    return redirect(url_for('staff'))

@app.route('/close_class', methods=['POST'])
def close_class():
    staff_user_id = session.get('user_id')
    if staff_user_id:
        current_datetime = get_current_datetime()
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                # Update the out_time for all students who haven't recorded it yet
                cur.execute("""
                    UPDATE attendance
                    SET out_time = %s
                    WHERE staff_id = %s AND out_time IS NULL
                """, (current_datetime, staff_user_id))

                # Set the QR code to None for the staff member
                cur.execute("""
                    UPDATE staffs
                    SET qr_code = NULL
                    WHERE staff_id = %s
                """, (staff_user_id,))
                
                conn.commit()
                session['qr_image_base64'] = False
                flash('Class closed, leave time recorded for all students, and QR code deleted.','success')
            except psycopg2.Error as e:
                print(f"Database error: {e}")
            finally:
                conn.close()
        return redirect(url_for('staff'))
    return "Error: User not logged in", 401

def verify_sub_code(sem, department, subject_code):
    """
    Verifies if the given semester, department, and subject code combination is valid.
    
    Args:
        sem (str): The semester value.
        department (str): The department value.
        subject_code (str): The subject code value.

    Raises:
        ValueError: If the combination is not valid.
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        query = '''
            SELECT COUNT(*) FROM college
            WHERE semester = %s AND department = %s AND subject_code = %s
        '''
        cur.execute(query, (sem, department, subject_code))
        result = cur.fetchone()
        cur.close()
        if result[0] == 0:
            flash('Invalid combination of semester, department, and subject code.', 'danger')
            raise ValueError('Invalid combination of semester, department, and subject code.')
        return True
    except psycopg2.Error as e:
        flash('Database error occurred.', 'danger')
        raise ValueError(f'Database error: {e}')
    finally:
        conn.close()

@app.route('/filter_subject_codes', methods=['POST'])
def filter_subject_codes():
    sem = request.json.get('sem')
    department = request.json.get('department')

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Fetch subject codes based on selected semester and department
        cur.execute('''
            SELECT DISTINCT subject_code
            FROM college
            WHERE semester = %s AND department = %s
        ''', (sem, department))
        subject_codes = cur.fetchall()

        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if conn:
            conn.close()

    return jsonify({'success': True, 'subject_codes': subject_codes})

#========================================================================================================
                        #For Student
#========================================================================================================

# Define route for student home page
@app.route('/student')
def student():
    user_details = session_getting()
    return render_template('student.html', user_details=user_details)

def mark_attendance_for_student(student_user_id, staff_id,college_id,department,semester,subject_code):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            current_datetime = get_current_datetime()
            print("recording attendance")
            in_time = current_datetime
            # Extract the time component
            time_component = in_time.time()

            # Convert time component to string in HH:MM:SS format
            time_string = time_component.strftime('%H:%M:%S.%f')

            # Store the time string in the session
            session['join_time'] = time_string
            print("::::::::::::::::::::::::::::::::::::::::::::",time_string)
            out_time = None
            date = current_datetime.date()
            print(date,college_id,department,semester,subject_code, staff_id, student_user_id, in_time, out_time)
            cur.execute("""
                INSERT INTO attendance (date, college_id,department,semester,subject_code, staff_id, student_id, in_time, out_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (date,college_id,department,semester,subject_code, staff_id, student_user_id, in_time, out_time))
            conn.commit()
            print("Attendance recorded successfully.")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

@app.route('/upload_qr_code', methods=['POST'])
def upload_qr_code():
    if 'qr_code_image' not in request.files:
        flash('No file part','danger')
        return redirect(url_for('student'))
    
    qr_code_image = request.files['qr_code_image']
    if qr_code_image.filename == '':
        flash('No selected file','danger')
        return redirect(url_for('student'))
    print(qr_code_image)
    if qr_code_image:
        qr_code_data = decode_qr_code(qr_code_image).decode('utf-8')
        print("qr_code_data:", qr_code_data)

        staff_qr_codes = get_staff_qr_codes_from_db()
        print("staff_qr_codes:", staff_qr_codes)

        matched_staff_id = None
        for staff_id, staff_qr_code_data in staff_qr_codes.items():
            if qr_code_data == staff_qr_code_data:
                matched_staff_id = staff_id
                break

        if matched_staff_id:
            session['qr_verified'] = True
            session['verified_staff_id'] = matched_staff_id
            flash('QR code verified successfully!', 'success')
            session_update(qr_code_data)
            
                        
        else:
            session['qr_verified'] = False
            flash('QR code verification failed. Please try again.', 'danger')

    return redirect(url_for('student'))

def decode_qr_code(qr_code_image):
    qr_code_img = Image.open(qr_code_image)
    decoded_objects = decode(qr_code_img)
    if decoded_objects:
        qr_code_data = decoded_objects[0].data
        return qr_code_data
    return None

def get_staff_qr_codes_from_db():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT staff_id, qr_code FROM staffs ")
            staff_qr_codes = {row[0]: row[1] for row in cur.fetchall()}
            return staff_qr_codes
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return {}

@app.route('/join_class', methods=['POST'])
def join_class():
    student_user_id = session.get('user_id')
    print(student_user_id)
    if student_user_id:
        staff_id = session.get('verified_staff_id')
        college_id=session.get('college_id')
        department=session.get('department')
        semester=session.get('semester')
        subject_code=session.get('subject_code')
        if staff_id:
            mark_attendance_for_student(student_user_id, staff_id, college_id,department,semester,subject_code)
            session['attendance_recorded'] = True
            flash('You have joined the class.', 'success')
            return redirect(url_for('student'))
    flash('Error joining the class.', 'danger')
    return redirect(url_for('student'))

@app.route('/leave_class', methods=['POST'])
def leave_class():
    student_user_id = session.get('user_id')
    if student_user_id:
        record_leave_time(student_user_id)
        session['qr_verified'] = False
        session['attendance_recorded'] = False
        flash('You have left the class.', 'success')
        return redirect(url_for('student'))
    flash('Error leaving the class.', 'danger')
    return redirect(url_for('student'))

def record_leave_time(student_user_id):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            current_datetime = get_current_datetime()
            college_id = session.get('college_id')
            department = session.get('department')
            semester = session.get('semester')
            subject_code = session.get('subject_code')
            join_time = session.get('join_time')
            print("datas::::::",current_datetime,college_id,department,semester,subject_code,join_time)
            # Execute the UPDATE statement
            cur.execute("""
                UPDATE attendance
                SET out_time = %s
                WHERE student_id = %s AND 
                    college_id = %s AND 
                    department = %s AND 
                    semester = %s AND 
                    subject_code = %s AND 
                    in_time = %s AND
                    out_time IS NULL
            """, (current_datetime, student_user_id, college_id, department, semester, subject_code, join_time))

            # Get the number of rows affected
            num_rows_affected = cur.rowcount
            print(f"Number of rows affected: {num_rows_affected}")

            # Commit the transaction
            conn.commit()
            print("Leave time recorded successfully.")
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()


@app.route('/process_qr_code', methods=['POST'])
def process_qr_code():
    image_data = request.json.get('imageData')

    decoded_qr_code = decode_live_qr_code(image_data)

    if decoded_qr_code:
        print("decoded")
        image = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1])))
        save_path = os.path.join('static', 'images', 'captured_qr_code.png')
        image.save(save_path)

        staff_qr_codes = get_staff_qr_codes_from_db()
        matched_staff_id = None
        for staff_id, staff_qr_code_data in staff_qr_codes.items():
            if decoded_qr_code == staff_qr_code_data:
                matched_staff_id = staff_id
                break
        print(matched_staff_id)

        if matched_staff_id:
            session['qr_verified'] = True
            session['verified_staff_id'] = matched_staff_id
            flash('QR code verified successfully!', 'success')
            session_update(decoded_qr_code)
                        
            return jsonify({
                'success': True,
                'qr_code_data': decoded_qr_code,
                'image_path': save_path,
                'staff_id': matched_staff_id,
                'redirect_url': url_for('student')  # Ensure 'student' home page is the correct endpoint
            })
        else:
            session['qr_verified'] = False
            flash('QR code verification failed. Please try again.', 'danger')
            return jsonify({'success': False, 'message': 'QR code verification failed. Please try again.'})
    else:
        return jsonify({'success': False, 'message': 'Failed to decode QR code'})

def decode_live_qr_code(image_data):
    # Here you would have your implementation for decoding the QR code from the image_data
    # This is just a placeholder for the actual QR code decoding logic
    try:
        image = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1])))
        # Assuming you have a function that decodes QR code from the image
        # For example, using pyzbar or some other library to decode
        from pyzbar.pyzbar import decode
        decoded_objects = decode(image)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        else:
            return None
    except Exception as e:
        print(f"Error decoding QR code: {e}")
        return None
#========================================================================================================
                        #For Attendance 
#========================================================================================================

@app.route('/attendance_report', methods=['POST'])
def attendance_report():
    user_details = session_getting() 
    user_id = session.get('user_id')
    user_type = session.get('type')  # Assuming you have a user_type in the session to differentiate between student and staff
    print(user_id,user_type)
    if user_type == 'student':
        # Query attendance records for the student
        attendance_records = get_attendance_records_for_student(user_id)
        print(attendance_records)
    elif user_type == 'staff':
        # Query attendance records for the staff's students
        staff_id = user_id
        attendance_records = get_attendance_records_for_staff(staff_id)
    else:
        attendance_records = []
    college_id,departments,sem,subject_codes=college_table()
    

    return render_template('attendance_report.html', attendance_records=attendance_records,user_details=user_details, departments=departments, college=college_id,subject_codes=subject_codes,sem=sem)

def get_attendance_records_for_student(student_id):
    conn = get_db_connection()
    if conn:
        try:
            print(student_id)
            cur = conn.cursor()
            cur.execute("""
                SELECT date,college_id,department,semester,subject_code, staff_id, student_id, in_time, out_time, record
                FROM attendance
                WHERE student_id = %s
                ORDER BY date DESC
            """, (student_id,))
            records = cur.fetchall()
            print(records)
            return records
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return []

def get_attendance_records_for_staff(staff_id):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT date,college_id,department,semester,subject_code, staff_id, student_id, in_time, out_time, record
                FROM attendance
                WHERE staff_id = %s
                ORDER BY date DESC
            """, (staff_id,))
            records = cur.fetchall()
            return records
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    return []


if __name__ == '__main__':
    app.run(debug=False)
