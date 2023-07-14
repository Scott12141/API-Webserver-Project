from init import db, bcrypt
from flask import Blueprint
from models.user import User


db_commands = Blueprint('db',  __name__)

# auth_routes = Blueprint('auth', __name__, url_prefix='/auth')

# @auth_routes.route('/register')


@db_commands.cli.command('drop')
def drop_db():
    db.drop_all()
    print('Tables Dropped')

@db_commands.cli.command('create')
def create_db():
    db.create_all()
    print('Tables Created')

@db_commands.cli.command('seed')
def seed_db():
    users = [
        User(
            first_name = 'Scott',
            last_name = 'Taylor',
            email = 'admin@mail.com',
            password = bcrypt.generate_password_hash('password123').decode('utf-8'),
            is_admin = True,
        ),
        User(
            first_name = 'Jane',
            last_name = 'Doe',
            address = '1 John Street, Vic, 3999',
            email = 'janedoe@mail.com',
            password = bcrypt.generate_password_hash('jane123').decode('utf-8'),
        ),
        User(
            first_name = 'John',
            last_name = 'Smith',
            address = '1 Jane Street, Vic, 3999',
            email = 'johnsmith@mail.com',
            password = bcrypt.generate_password_hash('john123').decode('utf-8'),
        )
    ]

    db.session.add_all(users)
    db.session.commit()

    print("Tables Seeded")