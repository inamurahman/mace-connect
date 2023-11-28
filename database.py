from sqlalchemy import create_engine, text
import os

ssl_args = {'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'}}
db_string = os.environ.get('DB_CONNECTION_MACEDB')
print(db_string)
engine = create_engine(db_string, connect_args=ssl_args)


def load_user_from_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT UserID,Username,Password,UserType FROM Users"))
        users = result.all()

        users = {user[1]: {'password': user[2], 'usertype': user[3]} for user in users}

    return users