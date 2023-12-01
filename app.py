from flask import Flask, jsonify, render_template, redirect, url_for, request, session, make_response, send_file
from functools import wraps
from database import *
from sqlalchemy import text, create_engine
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO

import os
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_MACEDB')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'}}
}
db = SQLAlchemy(app)

from flask_sqlalchemy import SQLAlchemy

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=False)
    document_filename = db.Column(db.String(255), nullable=False)
    image_content = db.Column(db.LargeBinary)  # Assuming BLOB type
    document_content = db.Column(db.LargeBinary)  # Assuming BLOB type
    upload_date = db.Column(db.TIMESTAMP, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, image_filename, document_filename, image_content, document_content):
        self.image_filename = image_filename
        self.document_filename = document_filename
        self.image_content = image_content
        self.document_content = document_content

# Now you can use this model for database operations



# events = [{'id': 1, 'name': 'takshak', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue':'Seminar hall 2'}, {'id': 2, 'name': 'sanskriti', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue':'ootpra'}, {'id': 3, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 4, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 5, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 6, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}]

# users = {'trial@gmail.com': {'password': 'secret', 'type':'admin'}}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return render_template('login.html', error="You need to login first")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if session['usertype'] == 'admin':
            category = request.form['category']
            if category == 'All':
                events = load_events_from_db()
                return render_template('home.html', events=events, usertype=session['usertype'], username=session['username'],categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
            events = load_events_from_db()
            events = [event for event in events if event['category'] == request.form['category']]
            return render_template('home.html', events=events, usertype=session['usertype'], username=session['username'],categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
        if session['usertype'] == 'organizer':
            category = request.form['category']
            if category == 'All':
                events = load_events_from_db()
                return render_template('home.html', events=events, usertype=session['usertype'], username=session['username'],categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
            events = load_events_from_db()
            events = [event for event in events if event['category'] == request.form['category']]
            return render_template('home.html', events=events, usertype=session['usertype'], username=session['username'],categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
        if session['usertype'] == 'faculty':
            category = request.form['category']
            if category == 'All':
                events = load_events_from_db()
                return render_template('home.html', events=events, usertype=session['usertype'], username=session['username'],categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
            events = load_events_from_db()
            events = [event for event in events if event['category'] == request.form['category']]
            return render_template('home.html', events=events, usertype=session['usertype'], username=session['username'],categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
        return "You are not authorized to perform this action", 403
    events = load_events_from_db()
    return render_template('home.html', events=events, usertype=session['usertype'], username=session['username'],category_list=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
@app.route('/events/<int:event_id>')
@login_required
def event(event_id):
    events = load_events_from_db()
    specific_event = next(event for event in events if event['eventid'] == event_id)
    specific_event['email'] = get_organizer_email(specific_event['organizerid'])
    eventhead = get_eventhead_details(specific_event['head'])
    specific_event['eventhead'] = eventhead['firstname'] + " " + eventhead['lastname']
    specific_event['mobile'] = eventhead['mobile']
    print(specific_event)
    if specific_event:
        return render_template('event.html', event=specific_event,remarkFaculty=get_remark_faculty(event_id))
    else:
        return "Event not found", 404
    
@app.route('/events/<int:event_id>/approve', methods=[ 'POST'])
@login_required
def approve_event(event_id):
    if request.method == 'POST':
        if session['usertype'] == 'faculty':
            remark = request.form['remarks']
            approverid = get_user_id(session['username'])
            with engine.connect() as connection:
                stmt = text("insert into Approval (ApprovalStatus, ApproverID, Remarks, EventID) values ('Approved', :approver, :remark, :eventid)").bindparams(approver=approverid, remark=remark, eventid=event_id)
                result = connection.execute(stmt)
                stmt = text("UPDATE Events SET CurrentStage='admin' WHERE EventID=:eventid").bindparams(eventid=event_id)
                result = connection.execute(stmt)
            return redirect(url_for('home'))
        
        if session['usertype'] != 'admin':
            return "You are not authorized to perform this action", 403
        
        remark = request.form['remarks']
        with engine.connect() as connection:
            stmt = text("UPDATE Events SET ApprovalStatus='approved', Remarks=:remark WHERE EventID=:eventid").bindparams(remark=remark, eventid=event_id)
            result = connection.execute(stmt)
            stmt = text("UPDATE Events SET CurrentStage='final' WHERE EventID=:eventid").bindparams(eventid=event_id)
        return redirect(url_for('home'))
    return "Invalid request", 404

@app.route('/events/<int:event_id>/reject', methods=[ 'POST'])
@login_required
def reject_event(event_id):
    if session['usertype'] == 'faculty':
        remark = request.form['remarks']
        approverid = get_user_id(session['username'])

        with engine.connect() as connection:
            stmt = text("insert into Approval (ApprovalStatus, ApproverID, Remarks, EventID) values ('Rejected', :approver, :remark, :eventid)").bindparams(approver=approverid, remark=remark, eventid=event_id)
            result = connection.execute(stmt)
            stmt = text("UPDATE Events SET CurrentStage='faculty' WHERE EventID=:eventid").bindparams(eventid=event_id)
            result = connection.execute(stmt)
        return redirect(url_for('home'))
    
    if session['usertype'] != 'admin':
        return "You are not authorized to perform this action", 403


    remark = request.form['remarks']
    with engine.connect() as connection:
        stmt = text("UPDATE Events SET ApprovalStatus='Rejected', Remarks=:remark WHERE EventID=:eventid").bindparams(remark=remark, eventid=event_id)
        result = connection.execute(stmt)
        stmt = text("UPDATE Events SET CurrentStage='organizer' WHERE EventID=:eventid").bindparams(eventid=event_id)
        result = connection.execute(stmt)
    return redirect(url_for('home'))                 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        
        if request.cookies.get('username'): 
            return redirect(url_for('home'))
        return render_template('login.html', error=None)
    
    

    username = request.form['username']
    password = request.form['password']
    remember_me = 'remember_me' in request.form

    user = get_user(username)
    if user is None:
        return render_template('login.html', error="Invalid username or password")

    if user['password'] == password:
        session['username'] = user['username']
        session['usertype'] = user['usertype']
        if remember_me:
            session.permanent = True
            response = make_response(redirect(url_for('home')))
            response.set_cookie('username', username, max_age=30*24*60*60)
            response.set_cookie('usertype', user['usertype'], max_age=30*24*60*60)
            return response

        return redirect(url_for('home'))
    
        
    return render_template('login.html', error="Invalid username or password")


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('usertype', None)
    return render_template('login.html', error="You have been logged out")

@app.route('/api/events')
def api_events():
    events = load_events_from_db()
    return jsonify(events)

@app.route('/signup')
def signup():
    return render_template('signup.html')
    

@app.route('/requests', methods=['GET', 'POST'])
@login_required
def requests():
    if request.method == 'POST':
        if session['usertype'] == 'admin':
            events = filter_events_by_status(request.form['status'])
            events = [event for event in events if event['currentstage'] == 'admin']
            return render_template('requests.html', events=events)
        if session['usertype'] == 'organizer':
            events = filter_events_by_status(request.form['status'])
            events = [event for event in events if event['organizerid'] == get_user_id(session['username'])]
            return render_template('requests.html', events=events)
        if session['usertype'] == 'faculty':
            events = filter_events_by_status(request.form['status'])
            events = [event for event in events if event['faculty'] == session['username']]
            return render_template('requests.html', events=events)
        return "You are not authorized to perform this action", 403
    
    if session['usertype'] == 'faculty':
        events = load_events_from_db()
        events = [event for event in events if event['faculty'] == session['username']]
        return render_template('requests.html', events=events)
    if session['usertype'] == 'admin':
        events = load_events_from_db()
        events = [event for event in events if event['currentstage'] == 'admin']
        return render_template('requests.html', events=events)
    if session['usertype'] == 'organizer':
        events = load_events_from_db()
        events = [event for event in events if event['organizerid'] == get_user_id(session['username'])]
        return render_template('requests.html', events=events)
    return "You are not authorized to perform this action", 403

@app.route('/clubs')
@login_required
def clubs():
    return render_template('clubs.html', clubs=load_organizers_from_db())
    

@app.route('/signup/<string:usertype>', methods=['GET', 'POST'])
def signup_form(usertype):
    types = ['student', 'faculty', 'organizer']
    if usertype not in types:
        return "Invalid user type", 404
    if request.method == 'GET':
        classes = ['S1DS','S1CS','S1ME','S2DS','S2CS','S2ME','S3DS','S3CS','S3ME','S4DS','S4CS','S4ME','S5DS','S5CS','S5ME','S6DS','S6CS','S6ME','S7DS','S7CS','S7ME','S8DS','S8CS','S8ME']
        departments = ['Computer Science', 'Mechanical', 'Electrical', 'Electronics', 'Civil']
        return render_template('signupForm.html', usertype=usertype, faculties=load_faculty_from_db(),  classlist=classes, deptlist=departments)
    
    users = load_user_from_db()
    if usertype == 'student':
        print(request.form)
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        fname = request.form['firstname']
        lname = request.form['lastname']
        batch = request.form['class']
        mobile = request.form['mobile']
        if username in users:
            return render_template('signupForm.html', usertype=usertype, error="Username already exists")
        with engine.connect() as connection:
            stmt = text("INSERT INTO Users (Username, Password, UserType, Email) VALUES (:user, :passwd, :type, :mail )").bindparams(user=username, passwd=password, type=usertype, mail=email)
            result = connection.execute(stmt)
            stmt = text("INSERT INTO UserDetails (FirstName, LastName, Class, Mobile, UserID) VALUES (:fname, :lname, :batch, :mobile, :id)").bindparams(fname=fname, lname=lname, batch=batch, mobile=mobile, id=get_user_id(username))
            result = connection.execute(stmt)
        return redirect(url_for('login'))
    
    elif usertype == 'faculty':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        fname = request.form['firstname']
        lname = request.form['lastname']
        mobile = request.form['mobile']
        dept = request.form['dept']
        if username in users:
            return render_template('signupForm.html', usertype=usertype, error="Username already exists")
        
        with engine.connect() as connection:
            stmt = text("INSERT INTO Users (Username, Password, UserType, Email) VALUES (:user, :passwd, :type, :mail )").bindparams(user=username, passwd=password, type=usertype, mail=email)
            result = connection.execute(stmt)
            stmt = text("INSERT INTO UserDetails (FirstName, LastName, Department, Mobile, UserID) VALUES (:fname, :lname, :dept, :mobile, :id)").bindparams(fname=fname, lname=lname, dept=dept, mobile=mobile, id=get_user_id(username))
            result = connection.execute(stmt)
        return redirect(url_for('login'))
    
    elif usertype == 'organizer':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        orgname = request.form['orgname']
        orgdesc = request.form['orgdesc']
        facultyadv = request.form['faculty']
        
        with engine.connect() as connection:
            stmt = text("INSERT INTO Users (Username, Password, UserType, Email) VALUES (:user, :passwd, :type, :mail )").bindparams(user=username, passwd=password, type=usertype, mail=email)
            result = connection.execute(stmt)
            stmt = text("INSERT INTO Organizer (OrganizerName, Description, AdvisorUsername, Username, UserID) VALUES (:orgname, :orgdesc, :facultyadv, :username, :userid)").bindparams(orgname=orgname, orgdesc=orgdesc, facultyadv=facultyadv, username=username, userid=get_user_id(username))
            result = connection.execute(stmt)
        return redirect(url_for('login', error="You have been registered as an organizer. Please login to continue"))

@app.route('/createevent', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'GET':
        return render_template('createevent.html', faculties=load_faculty_from_db(),categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
    
    name = request.form['name']
    date = request.form['date']
    description = request.form['desc']
    venue = request.form['venue']
    eventhead = request.form['eventhead']
    category = request.form['category']
    faculty = request.form['faculty']
    image = request.files['image']
    time = request.form['time']
    document = request.files['document']
    newFile = UploadedFile(image_filename=image.filename, document_filename=document.filename, image_content=image.read(), document_content=document.read())
    db.session.add(newFile)
    db.session.commit()
    file_id = newFile.id
    if check_username(eventhead) == False:
        return render_template('createevent.html', faculties=load_faculty_from_db(),categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'], error="Event head not found")
    with engine.connect() as connection:
        smtp = text("INSERT INTO Events (EventName, Date, Description, Location, Category, OrganizerID, RequestedBy, fileid, head, Time, CurrentStage) VALUES (:name, :date, :description, :venue, :category,:organizerid,:faculty, :fileid, :head, :time, 'faculty')").bindparams(name=name, date=date, description=description, venue=venue, category=category, organizerid=get_user_id(session['username']), faculty=faculty, fileid=file_id, head=eventhead, time=time)
        result = connection.execute(smtp)
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    image = request.files['image']
    document = request.files['document']
    newFile = UploadedFile(image_filename=image.filename, document_filename=document.filename, image_content=image.read(), document_content=document.read())
    db.session.add(newFile)
    db.session.commit()
    return 'File saved to database!'

@app.route('/view/image/<int:file_id>')
@login_required
def view_image(file_id):
    file_data = UploadedFile.query.filter_by(id=file_id).first()
    return send_file(BytesIO(file_data.image_content), download_name=file_data.image_filename)


@app.route('/view/document/<int:file_id>')
@login_required
def view_document(file_id):
    file_data = UploadedFile.query.filter_by(id=file_id).first()
    return send_file(BytesIO(file_data.document_content), download_name=file_data.document_filename)

@app.route('/download/image/<int:file_id>')
@login_required
def download_image(file_id):
    file_data = UploadedFile.query.filter_by(id=file_id).first()
    return send_file(BytesIO(file_data.image_content), download_name=file_data.image_filename, as_attachment=True)


@app.route('/download/document/<int:file_id>')
@login_required
def download_document(file_id):
    file_data = UploadedFile.query.filter_by(id=file_id).first()
    return send_file(BytesIO(file_data.document_content), download_name=file_data.document_filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)