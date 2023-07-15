from init import db
from flask import Blueprint, request
from models.product import Product, product_schema, products_schema
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

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
        return {'error': f'Product not found with id {id}'}, 404
    
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
            return {'error': f'{err.orig.diag.column_name} is required for Product creation'}, 409


# NEEDS IS_ADMIN TO DELETE!!!!
@products_bp.route('/<int:id>', methods = ['DELETE'])
def delete_product(id):
    qry = db.select(Product).where(Product.id == id)
    product = db.session.scalar(qry)
    if product:
        db.session.delete(product)
        db.session.commit()
        return {'message': f"Product {product.name} deleted successfully"}
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
        return {'error': f'Product with id {id} not found'}, 404