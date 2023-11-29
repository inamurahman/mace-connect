from flask import Flask, jsonify, render_template, redirect, url_for, request, session, make_response
from functools import wraps
from database import engine, load_user_from_db, get_user_id, get_user, load_faculty_from_db
from sqlalchemy import text
import os
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


events = [{'id': 1, 'name': 'takshak', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue':'Seminar hall 2'}, {'id': 2, 'name': 'sanskriti', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue':'ootpra'}, {'id': 3, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 4, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 5, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 6, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}]

# users = {'trial@gmail.com': {'password': 'secret', 'type':'admin'}}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return render_template('login.html', error="You need to login first")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    return render_template('home.html', events=events)

@app.route('/events/<int:event_id>')
@login_required
def event(event_id):
    specific_event = next((event for event in events if event['id'] == event_id), None)
    if specific_event:
        return render_template('event.html', event=specific_event)
    else:
        return "Event not found", 404

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

    if user['password'] == password:
        session['username'] = user['username']
        session['usertype'] = user['usertype']
        if remember_me:
            session.permanent = True
            response = make_response(redirect(url_for('home')))
            response.set_cookie('username', username, max_age=30*24*60*60)
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
    return jsonify(events)

@app.route('/signup')
def signup():
    return render_template('signup.html')
    
    

@app.route('/signup/<string:usertype>', methods=['GET', 'POST'])
def signup_form(usertype):
    types = ['student', 'faculty', 'organizer']
    if usertype not in types:
        return "Invalid user type", 404
    if request.method == 'GET':
        classes = ['S1DS','S1CS','S1ME','S2DS','S2CS','S2ME','S3DS','S3CS','S3ME','S4DS','S4CS','S4ME','S5DS','S5CS','S5ME','S6DS','S6CS','S6ME','S7DS','S7CS','S7ME','S8DS','S8CS','S8ME']
        departments = ['Computer Science', 'Mechanical', 'Electrical', 'Electronics', 'Civil']
        return render_template('signupForm.html', usertype=usertype,  classlist=classes, deptlist=departments)
    
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
            stmt = text("INSERT INTO Organizer (OrganizerName, Description, AdvisorUsername, UserID) VALUES (:orgname, :orgdesc, :facultyadv)").bindparams(orgname=orgname, orgdesc=orgdesc, facultyadv=facultyadv)
        return redirect(url_for('login'))

@app.route('/createevent', methods=['GET', 'POST'])
def create_event():
    if request.method == 'GET':
        return render_template('createevent.html', faculties=load_faculty_from_db(),categorylist=['Technical', 'Cultural', 'Sports', 'Workshop', 'Seminar', 'Other'])
    
    name = request.form['name']
    date = request.form['date']
    description = request.form['description']
    venue = request.form['venue']
    category = request.form['category']
    faculty = request.form['faculty']

    with engine.connect() as connection:
        smtp = text("INSERT INTO Events (EventName, Date, Description, Location, Category, OrganizerID, RequestedBy) VALUES (:name, :date, :description, :venue, :category, :organizerid)").bindparams(name=name, date=date, description=description, venue=venue, category=category, organizerid=get_user_id(session['username'], faculty=faculty))
        result = connection.execute(smtp)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)