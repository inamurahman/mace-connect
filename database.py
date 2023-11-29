from sqlalchemy import create_engine, text
import os

ssl_args = {'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'}}
db_string = os.environ.get('DB_CONNECTION_MACEDB')
engine = create_engine(db_string, connect_args=ssl_args)


def load_user_from_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT UserID,Username,Password,UserType FROM Users"))
        users = result.all()

        users = {user[1]: {'password': user[2], 'usertype': user[3],'userid': user[0]} for user in users}

    return users

def get_user_id(username):
    with engine.connect() as connection:
        stmt = text("SELECT UserID FROM Users WHERE Username=:username").bindparams(username=username)
        result = connection.execute(stmt)
        user_id = result.first()[0]
    return user_id

def get_user(username):
    with engine.connect() as connection:
        stmt = text("SELECT UserID,Username,Password,UserType FROM Users WHERE Username=:username").bindparams(username=username)
        result = connection.execute(stmt)
        user = result.first()
        if user is None:
            return None
        user = {'userid': user[0], 'username': user[1], 'password': user[2], 'usertype': user[3]}
    return user 

def load_faculty_from_db():
    with engine.connect() as connection:
        smtp = text("SELECT Users.username, UserDetails.UserID, UserDetails.FirstName, UserDetails.LastName, UserDetails.Mobile, UserDetails.Department FROM UserDetails JOIN Users ON UserDetails.UserID = Users.UserID WHERE UserDetails.UserID IN (SELECT UserID FROM Users WHERE UserType='faculty');")
        result = connection.execute(smtp)
        faculty = result.all()
        faculty = [{'username': user[0], 'userid': user[1], 'firstname': user[2], 'lastname': user[3], 'mobile': user[4], 'department': user[5]} for user in faculty]
    return faculty

def load_events_from_db():
    with engine.connect() as connection:
        smtp = text("SELECT * FROM Events")
        result = connection.execute(smtp)
        events = result.all()
        events = [{'eventid': event[0], 'name': event[1], 'date': event[2], 'description': event[3], 'category': event[4], 'organizer': event[5]} for event in events]
    return events