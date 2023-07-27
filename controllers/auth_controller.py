from init import db, bcrypt
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from models.user import User, user_schema
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from datetime import timedelta


auth_bp = Blueprint('auth', __name__, url_prefix = '/auth')

@auth_bp.route('/register', methods = ['POST'])
def auth_register():
    try:
        # retrieve JSON data parsed into the body from the front end as a python object and store it in body_data
        body_data = user_schema.load(request.get_json())
        # then extract that JSON data posted to the front end into the users model imported from the user models to create the user in the back end (database)
        user = User()
        user.first_name = body_data.get('first_name')
        user.last_name = body_data.get('last_name')
        user.address = body_data.get('address')
        user.email = body_data.get('email')
        # Hashes the users password to be stored in the database as a hash
        if body_data.get('password'):
            user.password = bcrypt.generate_password_hash(body_data.get('password')).decode('utf-8')
        # Adds this user to the session
        db.session.add(user)
        # Commits user that was added to the database
        db.session.commit()
        # Now send a message to the front end in json form with what data was stored in the back end(database)
        return user_schema.dump(user), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {'error': 'This email address has already been registered please use another one'}, 409
        elif err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {'error': f'Your {err.orig.diag.column_name} is required for registration'}, 409



@auth_bp.route('/login', methods = ['POST'])
def auth_login():
    # retrieve JSON data parsed into the body from the front end as a python object and store it in body_data
    body_data = request.get_json()
    # Query the database to find a user by their email address
    qry = db.select(User).filter_by(email = body_data.get('email'))
    user = db.session.scalar(qry)
    # If the query from the DB returns a valid email then check the password hash on the DB and return a token for the user
    # If the query of the DB doesnt match a valid user email then return email error message
    # If the valid email matches but the password hash doesnt return password error message
    if user:
        if bcrypt.check_password_hash(user.password, body_data.get('password')):
            token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
            return {'email': user.email, 'token': token}
        else:
            return {'error': "password was incorrect, please try again"}, 401
    else:
        return {'error': "email does not exist, please try again"}, 401
    
    