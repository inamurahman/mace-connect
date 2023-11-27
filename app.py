from flask import Flask, jsonify, render_template, redirect, url_for, request, session, make_response
from functools import wraps
from database import engine, load_user_from_db
from sqlalchemy import text

app = Flask(__name__)
app.secret_key = 'super secret string'


events = [{'id': 1, 'name': 'takshak', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue':'Seminar hall 2'}, {'id': 2, 'name': 'sanskriti', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue':'ootpra'}, {'id': 3, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 4, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 5, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}, {'id': 6, 'name': 'dj night', 'date': '2019-01-01', 'description':"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor", 'venue': 'basket ball court'}]



# users = {'trial@gmail.com': {'password': 'secret', 'type':'admin'}}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return {{url_for('login')}}
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
        return render_template('login.html', error=None)
    
    users = load_user_from_db()

    email = request.form['email']
    password = request.form['password']
    remember_me = 'remember_me' in request.form
    if email in users and users[email]['password'] == password:
        session['username'] = email
        if remember_me:
            session.permanent = True
            response = make_response(redirect(url_for('home')))
            response.set_cookie('username', email, max_age=30*24*60*60)
            return response

        return redirect(url_for('home'))
    
        
    return render_template('login.html', error="Invalid username or password")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return "Logged out"

@app.route('/api/events')
def api_events():
    return jsonify(events)

    
if __name__ == "__main__":
    app.run(debug=True)