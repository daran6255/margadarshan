from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify
import logging
from mysql.connector import pooling
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

load_dotenv(override=True)


EMAIL_DOMAIN = 'smtp.ipage.com'
EMAIL_PORT = '587'
EMAIL_ADDRESS = 'margadarshan@winvinayafoundation.org'
EMAIL_PASSWORD = 'Margadarshan123'

# MySQL Configuration
dbconfig = {
    "host": os.getenv('DB_HOST'),
    "port": os.getenv('DB_PORT'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DB_NAME'),
}

# Increase pool size if needed
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool",
                                      pool_size=32,  # Increase if necessary
                                      **dbconfig)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/search')
def search():
    search_query = request.args.get('query', '').strip()

    query = "SELECT * FROM candidates WHERE name LIKE %s"
    cnx = cnxpool.get_connection()
    try:
        cur = cnx.cursor()
        cur.execute(query, ('%' + search_query + '%',))
        students = cur.fetchall()
    finally:
        cur.close()
        cnx.close()

    return render_template('student_profiles.html', students=students)

@app.route('/')
def home():
    events = get_upcoming_events()
    event_schedule = get_events_schedule()
    students = get_students_profile()
    return render_template('home.html', events=events, event_schedule=event_schedule, students=students)

def get_upcoming_events():
    cnx = cnxpool.get_connection()
    try:
        cur = cnx.cursor()
        cur.execute("SELECT title, date, location FROM events ORDER BY date ASC LIMIT 3")
        events = cur.fetchall()
    finally:
        cur.close()
        cnx.close()
    return events
@app.route('/event-schedule')
def get_events_schedule():
    cnx = cnxpool.get_connection()
    try:
        cur = cnx.cursor()
        cur.execute('SELECT * FROM event_schedule')
        event_schedule = cur.fetchall()
    finally:
        cur.close()
        cnx.close()
    return event_schedule

def get_students_profile():
    cnx = cnxpool.get_connection()
    try:
        cur = cnx.cursor()
        cur.execute('SELECT * FROM candidates')
        students = cur.fetchall()
    finally:
        cur.close()
        cnx.close()
    return students

@app.route('/register_corporate', methods=['POST'])
def register_corporate():
    company_name = request.form['corporateName']
    emailTo = request.form['corporateEmail']
    phone = request.form['corporatePhone']
    
    smtplibObj = smtplib.SMTP(EMAIL_DOMAIN, 587)
    smtplibObj.starttls()
    smtplibObj.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = emailTo
    msg['Subject'] ='Corporate Registration Confirmation'

    html = render_template('corporate_email_template.html', 
                               company_name=company_name, 
                               email=emailTo, 
                               phone=phone)
    
    msg.attach(MIMEText(html, 'html'))
    smtplibObj.send_message(msg)

    del msg
    smtplibObj.quit()

    # mail.send(msg)
    print('Registration successful, a confirmation email has been sent.')
    return redirect(url_for('home'))

@app.route('/register_student', methods=['POST'])
def register_student():
    student_name = request.form['studentName']
    emailTo = request.form['studentEmail']
    phone = request.form['studentPhone']
    
    smtplibObj = smtplib.SMTP(EMAIL_DOMAIN, 587)
    smtplibObj.starttls()
    smtplibObj.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = emailTo
    msg['Subject'] ='Student Registration Confirmation'

    html = render_template('student_email_template.html', 
                               student_name=student_name, 
                               email=emailTo, 
                               phone=phone)
    
    msg.attach(MIMEText(html, 'html'))
    smtplibObj.send_message(msg)

    del msg
    smtplibObj.quit()

    # mail.send(msg)
    print('Registration successful, a confirmation email has been sent.')
    return redirect(url_for('home'))

def insert_event(title, date, location):
    cnx = cnxpool.get_connection()
    try:
        cur = cnx.cursor()
        query = "INSERT INTO events (title, date, location) VALUES (%s, %s, %s)"
        cur.execute(query, (title, date, location))
        cnx.commit()
    finally:
        cur.close()
        cnx.close()

@app.route('/add-events', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        location = request.form['location']
        insert_event(title, date, location)
        return redirect(url_for('add_event'))
    return render_template('add_event.html')

@app.route('/index')
def index():
    category = request.args.get('category', 'all')
    disability = request.args.get('disability', 'all')
    domain = request.args.get('domain', 'all')
    experience = request.args.get('experience', 'all')
    search = request.args.get('search', '')

    query = "SELECT * FROM candidates WHERE 1=1"
    params = {}

    if category and category != 'all':
        query += " AND category = %(category)s"
        params['category'] = category
    
    if disability and disability != 'all':
        query += " AND disability_type = %(disability)s"
        params['disability'] = disability
    
    if domain and domain != 'all':
        query += " AND domain = %(domain)s"
        params['domain'] = domain
    
    if experience and experience != 'all':
        query += " AND experience = %(experience)s"
        params['experience'] = experience

    if search:
        query += " AND name LIKE %(search)s"
        params['search'] = f"%{search}%"

    cnx = cnxpool.get_connection()
    try:
        cur = cnx.cursor()
        cur.execute(query, params)
        students = cur.fetchall()
    finally:
        cur.close()
        cnx.close()

    return render_template('index.html', students=students)

@app.route('/download_resume/<filename>')
def download_resume(filename):
    resume_path = os.path.join('static/uploads/resume', filename)
    if os.path.exists(resume_path):
        return send_from_directory(directory='static/uploads/resume', path=filename, as_attachment=True)
    else:
        return 'Resume not found', 404

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    pdf_path = os.path.join('static/uploads/pdf', filename)
    if os.path.exists(pdf_path):
        return send_from_directory(directory='static/uploads/pdf', path=filename, as_attachment=True)
    else:
        return 'PDF not found', 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'info@winvinayafoundation.org' and password == 'Winvinaya@123&':
            session['email'] = email
            return redirect(url_for('home_admin'))
        else:
            error = 'Invalid email or password. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/home-admin')
@login_required
def home_admin():
    cnx = cnxpool.get_connection()
    try:
        cur = cnx.cursor()
        cur.execute("SELECT * FROM candidates")
        students = cur.fetchall()
    finally:
        cur.close()
        cnx.close()

    return render_template('homeadmin.html', students=students)

@app.route('/update_candidate', methods=['POST'])
@login_required
def update_candidate():
    data = request.form.to_dict()
    id = int(data['id'])
    name = data['name']
    age = int(data['age'])
    gender = data['gender']
    phone = data['phone']
    email = data['email']
    category = data['category']
    disability_type = data['disability']
    disability_percentage = int(data['percentage']) if data['percentage'] else None
    highest_qualification = data['qualification']
    department = data['department']
    graduation_year = int(data['graduation-year'])
    domain = data['domain']
    skills = data['skills']
    typing_speed = data['typing-speed']
    quality = data['quality']
    experience = data['experience']

    params = (
        name, age, gender, phone, email, category, disability_type, disability_percentage, highest_qualification, 
        department, graduation_year, domain, skills, typing_speed, quality, experience, id
    )

    cnx = cnxpool.get_connection()
    try:
        cur = cnx.cursor()
        cur.execute("""
            UPDATE candidates SET
                name=%s, age=%s, gender=%s, phone=%s, email=%s, category=%s, disability_type=%s, disability_percentage=%s, 
                highest_qualification=%s, department=%s, graduation_year=%s, domain=%s, skills=%s, typing_speed=%s, 
                quality=%s, experience=%s
            WHERE id=%s
        """, params)
        cnx.commit()
    finally:
        cur.close()
        cnx.close()

    return jsonify({"status": "success"})

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        category = request.form['category']
        disability = request.form.get('disability')
        disability_percentage = request.form['percentage']

        if not disability_percentage:
            disability_percentage = None
        else:
            try:
                disability_percentage = float(disability_percentage)
            except ValueError:
                return render_template('admin.html', error="Invalid disability percentage. Must be a decimal number.")

        qualification = request.form['qualification']
        department = request.form['department']
        graduation_year = request.form['graduation-year']
        domain = request.form['domain']
        skills = request.form['skills']
        typing_speed = request.form['typing-speed']
        quality = request.form['quality']
        experience = request.form['experience']
        photo = request.files['photo']
        pdf = request.files['pdf']
        resume = request.files['resume']
        video = request.files['video']

        photo.save(f'static/uploads/image/{photo.filename}')
        pdf.save(f'static/uploads/pdf/{pdf.filename}')
        resume.save(f'static/uploads/resume/{resume.filename}')
        video.save(f'static/uploads/video/{video.filename}')

        cnx = cnxpool.get_connection()
        try:
            cur = cnx.cursor()
            cur.execute("""
                INSERT INTO candidates (name, age, gender, phone, email, category, disability_type, disability_percentage, highest_qualification, department, graduation_year, domain, skills, typing_speed, quality, experience, photo, pdf, resume, video)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, age, gender, phone, email, category, disability, disability_percentage, qualification, department, graduation_year, domain, skills, typing_speed, quality, experience, photo.filename, pdf.filename, resume.filename, video.filename))
            cnx.commit()
        finally:
            cur.close()
            cnx.close()
        return redirect(url_for('index'))

    return render_template('admin.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    logging.basicConfig(level=logging.DEBUG)
    app.secret_key = 'supersecretkey'
    
