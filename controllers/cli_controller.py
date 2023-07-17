from init import db, bcrypt
from flask import Blueprint
from models.user import User
from models.product import Product
from models.comment import Comment


db_commands = Blueprint('db',  __name__)


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

    products = [
        Product(
            name = 'Celebration',
            description = 'Birthday, Anniversary etc.',
            price = 160.00,
            prep_days = 2
        ),
        Product(
            name = 'Wedding',
            description = 'Multi-tiered etc.',
            price = 450.00,
            prep_days = 5
        ),
        Product(
            name = 'Cupcakes',
            description = 'Various kinds by the dozen etc.',
            price = 35.00,
            prep_days = 1
        )
    ]
    db.session.add_all(products)

    comments = [
        Comment(
            message = "Birthday cake I bought looked so good and was delicious!",
            user = users[1],
            product = products[0]
        ),
        Comment(
            message = "I bought a 3 tiered weedding cake and it looked magnificent and tasted even better!",
            user = users[2],
            product = products[1]
        ),
        Comment(
            message = "Cupcake filling was so good, 10/10",
            user = users[1],
            product = products[2]
        )
    ]

    db.session.add_all(comments)

    db.session.commit()

    print("Tables Seeded")