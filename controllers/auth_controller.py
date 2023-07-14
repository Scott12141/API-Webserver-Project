from init import db, bcrypt
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from models.user import User, user_schema, users_schema
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes


auth_bp = Blueprint('auth', __name__, url_prefix = '/auth')

@auth_bp.route('/register', methods = ['POST'])
def auth_register():
    try:
        # retrieve data posted from the front end body in json format and store it in body_data
        body_data = request.get_json()
        # then extract that data to the users model imported from the user models to create the user in the back end (database)
        user = User()
        user.first_name = body_data.get('first_name')
        user.last_name = body_data.get('last_name')
        user.address = body_data.get('address')
        user.email = body_data.get('email')
        if body_data.get('password'):
            user.password = bcrypt.generate_password_hash(body_data.get('password')).decode('utf-8')

        db.session.add(user)
        db.session.commit()

        return user_schema.dump(user), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {'error': 'This email address has already been registered please use another one'}, 409
        elif err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {'error': f'Your {err.orig.diag.column_name} is required for registration'}, 409
