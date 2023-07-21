from init import db, jwt
from flask import Blueprint, request
from models.product import Product, product_schema, products_schema
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.comment import Comment, comment_schema, comments_schema
from models.order import Order, order_schema, orders_schema
from datetime import date

products_bp = Blueprint('products', __name__, url_prefix = '/products')


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
    
# NEEDS IS_ADMIN TO CREATE!!!!
@products_bp.route('/', methods = ['POST'])
def create_product():
    try:
        body_data = request.get_json()
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


# NEEDS IS_ADMIN TO DELETE!!!!
@products_bp.route('/<int:id>', methods = ['DELETE'])
def delete_product(id):
    qry = db.select(Product).where(Product.id == id)
    product = db.session.scalar(qry)
    if product:
        db.session.delete(product)
        db.session.commit()
        return {'message': f"Product {product.name} deleted successfully."}
    else:
        return {'error': f'Product with id {id} not found'}

# NEEDS IS_ADMIN TO UPDATE!!!!
@products_bp.route('/<int:id>', methods = ['PUT','PATCH'])
def update_product(id):
    body_data = request.get_json()
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
    








# Adding Comment controllers to Products controller as comments only exist on a Product entity

@products_bp.route('/<int:product_id>/comments', methods = ['POST'])
@jwt_required()
def create_comment(product_id):
    body_data = request.get_json()
    qry = db.select(Product).filter_by(id = product_id) 
    product = db.session.scalar(qry)
    if product:
        comment = Comment(
            message = body_data.get('message'),
            user_id = get_jwt_identity(),
            product = product
        )
        db.session.add(comment)
        db.session.commit()
        return comment_schema.dump(comment), 201
    else:
        return {'error': f'Product not found with id {product_id}.'}, 404
        

# No GET method for comments, all comments will exist and be related to products, so any GET product will display comments 


@products_bp.route('/<int:product_id>/comments/<int:comment_id>', methods = ['DELETE'])
@jwt_required()
def delete_comment(product_id, comment_id):
    qry = db.select(Comment).filter_by(id = comment_id)
    comment = db.session.scalar(qry)
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return {'message': f'Comment "{comment.message}" has been deleted successfully.'}
    else: 
        return {'error': f'Comment with id {comment_id} not found.'}, 404
    

@products_bp.route('/<int:product_id>/comments/<int:comment_id>', methods = ['PUT', 'PATCH'])
@jwt_required()
def edit_comment(product_id, comment_id):
    body_data = request.get_json()
    qry = db.select(Comment).filter_by(id = comment_id)
    comment = db.session.scalar(qry)
    if comment:
        comment.message = body_data.get('message') or comment.message
        db.session.commit()
        return comment_schema.dump(comment)
    else:
        return {'error': f'Comment with id {comment_id} not found.'}
