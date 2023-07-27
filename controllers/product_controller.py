from init import db, jwt
from flask import Blueprint, request
from models.product import Product, product_schema, products_schema
from models.user import User
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2 import errorcodes
from flask_jwt_extended import get_jwt_identity, jwt_required
from controllers.comment_controller import comments_bp


products_bp = Blueprint('products', __name__, url_prefix = '/products')
products_bp.register_blueprint(comments_bp)


@products_bp.route('/')
def get_products():
    # queries the database to retrieve and display all products with no filter
    qry = db.select(Product)
    # stores the query in product variable
    products = db.session.scalars(qry)
    return products_schema.dump(products)


@products_bp.route('/<int:id>')
def get_one_product(id):
    # queries the database in the products table where the product id matches what was parsed as the arguement to the function
    qry = db.select(Product).where(Product.id == id)
    # stores the query in product variable
    product = db.session.scalar(qry)
    # If a product by that id exists then return it in JSON format 
    if product:
        return product_schema.dump(product)
    # If a product by that id does not exist then return an error message
    else:
        return {'error': f'Product with id {id} not found.'}, 404
    

@products_bp.route('/', methods = ['POST'])
# JSON Web Token required from login to use this method
@jwt_required()
def create_product():
    try:
        # Checks to see if the user trying to post a product has is_admin attribute in the database
        is_admin = authorise_as_admin()
        # Only an admin can create products, checks to see if that condition has been met, if not return error message.
        if not is_admin:
            return {'error': 'Not authorised to create products'}, 401
        # retrieve JSON data parsed into the body from the front end as a python object and store it in body_data
        # load product schema for validation of parsed data
        body_data = product_schema.load(request.get_json())
        product = Product(
            name = body_data.get('name'),
            description = body_data.get("description"),
            price = body_data.get('price'),
            prep_days = body_data.get('prep_days')
        )
        db.session.add(product)
        # Commit added product to the database
        db.session.commit()
        return product_schema.dump(product), 201
    # Validates not null, unique and data type constraints
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {'error': f'{err.orig.diag.column_name} is required for Product creation.'}, 409
        elif err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {'error': 'A Product with this name already exists, please try another name'}, 409
    except DataError as err:
        if err.orig.pgcode == errorcodes.INVALID_TEXT_REPRESENTATION:
            return {'error': 'Please enter Price and/or Preperation days as a number.'}, 409


@products_bp.route('/<int:id>', methods = ['DELETE'])
# JSON Web Token required from login to use this method
@jwt_required()
def delete_product(id):
    # Checks to see if the user trying to delete a product has is_admin attribute in the database
    is_admin = authorise_as_admin()
    # Only an admin can delete products, checks to see if that condition has been met, if not return error message.
    if not is_admin:
        return {'error': 'Not authorised to delete products'}, 401
    # Query the database to find the product id parsed as the arguement of the fuction in the products table
    qry = db.select(Product).where(Product.id == id)
    # stores the query in product variable
    product = db.session.scalar(qry)
    # If the product id is found in the database the product will be deleted
    if product:
        db.session.delete(product)
        db.session.commit()
        return {'message': f"Product {product.name} deleted successfully."}, 200
    # If the product id is not found in the database an error message will be returned
    else:
        return {'error': f'Product with id {id} not found'}, 404


@products_bp.route('/<int:id>', methods = ['PUT','PATCH'])
# JSON Web Token required from login to use this method
@jwt_required()
def update_product(id):
    try:
        # Checks to see if the user trying to put/patch a product has is_admin attribute in the database
        is_admin = authorise_as_admin()
        # Only an admin can update products, checks to see if that condition has been met, if not return error message.
        if not is_admin:
            return {'error': 'Not authorised to update or modify products'}, 401
        # retrieve JSON data parsed into the body from the front end as a python object and store it in body_data
        # load product schema for validation of partially parsed data 
        body_data = product_schema.load(request.get_json(), partial = True)
        # Query the database to find the product id parsed as the arguement of the fuction in the products table
        qry = db.select(Product).where(Product.id == id)
        # stores the query in product variable
        product = db.session.scalar(qry)
        # If the product id is found in the database then the product can be updated with combination of the product fields
        if product:
            product.name = body_data.get('name') or product.name
            product.description = body_data.get("description") or product.description
            product.price = body_data.get('price') or product.price
            product.prep_days = body_data.get('prep_days') or product.prep_days
            db.session.commit()
            # Return the altered product schema for the product matching the id 
            return product_schema.dump(product), 201
        # If the product id is not found in the database an error message will be returned
        else:
            return {'error': f'Product with id {id} not found.'}, 404
    # Validates unique and data type constraints
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {'error': 'A Product with this name already exists, please try another name'}, 409
    except DataError as err:
        if err.orig.pgcode == errorcodes.INVALID_TEXT_REPRESENTATION:
            return {'error': 'Please enter Price and/or Preperation days as a number.'}, 409


def authorise_as_admin():
    # Check web token to get the user associated to that token
    user_id = get_jwt_identity()
    # Query the database to find the user id detected by the web token in the users table 
    # if the user has is_admin set as True then return that the user is admin
    qry = db.select(User).filter_by(id = user_id)
    user = db.session.scalar(qry)
    return user.is_admin