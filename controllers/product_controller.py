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
    products = db.session.scalars(qry)
    return products_schema.dump(products)


@products_bp.route('/<int:id>')
def get_one_product(id):
    # queries the database in the products table where the product id is equal to whatever id is passed into the front end as the argument
    qry = db.select(Product).where(Product.id == id)
    product = db.session.scalar(qry)
    if product:
        return product_schema.dump(product)
    else:
        return {'error': f'Product with id {id} not found.'}, 404
    

@products_bp.route('/', methods = ['POST'])
@jwt_required()
def create_product():
    try:
        is_admin = authorise_as_admin()
        if not is_admin:
            return {'error': 'Not authorised to create products'}
        body_data = product_schema.load(request.get_json())
        product = Product(
            name = body_data.get('name'),
            description = body_data.get("description"),
            price = body_data.get('price'),
            prep_days = body_data.get('prep_days')
        )
        db.session.add(product)
        db.session.commit()
        return product_schema.dump(product), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {'error': f'{err.orig.diag.column_name} is required for Product creation.'}, 409
        elif err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {'error': 'A Product with this name already exists, please try another name'}, 409
    except DataError as err:
        if err.orig.pgcode == errorcodes.INVALID_TEXT_REPRESENTATION:
            return {'error': 'Please enter Price and/or Preperation days as a number.'}, 409


@products_bp.route('/<int:id>', methods = ['DELETE'])
@jwt_required()
def delete_product(id):
    is_admin = authorise_as_admin()
    if not is_admin:
        return {'error': 'Not authorised to delete products'}
    qry = db.select(Product).where(Product.id == id)
    product = db.session.scalar(qry)
    if product:
        db.session.delete(product)
        db.session.commit()
        return {'message': f"Product {product.name} deleted successfully."}
    else:
        return {'error': f'Product with id {id} not found'}


@products_bp.route('/<int:id>', methods = ['PUT','PATCH'])
@jwt_required()
def update_product(id):
    try:
        is_admin = authorise_as_admin()
        if not is_admin:
            return {'error': 'Not authorised to update or modify products'}
        body_data = product_schema.load(request.get_json(), partial = True)
        qry = db.select(Product).where(Product.id == id)
        product = db.session.scalar(qry)
        if product:
            product.name = body_data.get('name') or product.name
            product.description = body_data.get("description") or product.description
            product.price = body_data.get('price') or product.price
            product.prep_days = body_data.get('prep_days') or product.prep_days
            db.session.commit()
            return product_schema.dump(product), 201
        else:
            return {'error': f'Product with id {id} not found.'}, 404
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {'error': 'A Product with this name already exists, please try another name'}, 409
    except DataError as err:
        if err.orig.pgcode == errorcodes.INVALID_TEXT_REPRESENTATION:
            return {'error': 'Please enter Price and/or Preperation days as a number.'}, 409


def authorise_as_admin():
    user_id = get_jwt_identity()
    qry = db.select(User).filter_by(id = user_id)
    user = db.session.scalar(qry)
    return user.is_admin