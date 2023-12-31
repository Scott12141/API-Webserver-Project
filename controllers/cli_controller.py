from init import db, bcrypt
from flask import Blueprint
from models.user import User
from models.product import Product
from models.comment import Comment
from models.order import Order
from datetime import date, timedelta


db_commands = Blueprint('db',  __name__)


@db_commands.cli.command('drop')
def drop_db():
    # Deletes all tables in the database
    db.drop_all()
    print('Tables Dropped')

@db_commands.cli.command('create')
def create_db():
    # Creates all tables in the database
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
            prep_days = 2,
            user = users[0]
        ),
        Product(
            name = 'Wedding',
            description = 'Multi-tiered etc.',
            price = 450.00,
            prep_days = 5,
            user = users[0]
        ),
        Product(
            name = 'Cupcakes x 6',
            description = 'Various kinds by the half-dozen etc.',
            price = 18.99,
            prep_days = 1,
            user = users[0]
        ),
        Product(
            name = 'Cupcakes x 12',
            description = 'Various kinds by the dozen etc.',
            price = 36.50,
            prep_days = 1,
            user = users[0]
        ),
        Product(
            name = 'Cupcakes x 18',
            description = 'Various kinds one and a half dozen etc.',
            price = 55.00,
            prep_days = 1,
            user = users[0]
        ),
        Product(
            name = 'Cupcakes x 24',
            description = 'Various kinds by the double-dozen etc.',
            price = 72.50,
            prep_days = 1,
            user = users[0]
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

    orders = [
        Order(
            date_ordered = date.today(),
            quantity = '1',
            status = 'In-queue',
            description = '2 tiered, red velvet, with white icing.',
            delivery_pup_date = date.today() + timedelta(days = 6),
            user = users[1],
            product = products[1]
        ),
        Order(
            date_ordered = date.today(),
            quantity = '1',
            status = 'In-queue',
            description = '6th Birthday spiderman mud cake for my son.',
            delivery_pup_date = date.today() + timedelta(days = 3),
            user = users[2],
            product = products[0]
        ),
        Order(
            date_ordered = date.today(),
            quantity = '1',
            status = 'In-queue',
            description = '6 x mars bar filling, 6 x snickers filling.',
            delivery_pup_date = date.today() + timedelta(days = 2),
            user = users[2],
            product = products[3]
        )
    ]

    db.session.add_all(orders)
    # Seeds all of the database entries 
    db.session.commit()

    print("Tables Seeded")