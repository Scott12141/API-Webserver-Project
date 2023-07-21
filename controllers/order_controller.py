from init import db, jwt
from flask import Blueprint, request
from models.order import Order, order_schema, orders_schema
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import date, timedelta, datetime
from models.product import Product
from controllers.product_controller import products_bp


orders_bp = Blueprint('orders', __name__, url_prefix = '/orders')


@orders_bp.route('/')
def get_orders():
    # queries the database to retrieve and display all products with no filter
    qry = db.select(Order)
    orders = db.session.scalars(qry)
    return orders_schema.dump(orders)


@orders_bp.route('/<int:id>')
def get_one_order(id):
    # queries the database in the products table where the product id is equal to whatever id is passed into the front end as the argument
    qry = db.select(Order).where(Order.id == id)
    order = db.session.scalar(qry)
    if order:
        return order_schema.dump(order)
    else:
        return {'error': f'Order with id {id} not found.'}, 404
    

@products_bp.route('/<int:product_id>/orders', methods = ['POST'])
@jwt_required()
def create_order(product_id):
    try:
        body_data = request.get_json()
        qry = db.select(Product).filter_by(id = product_id)
        product = db.session.scalar(qry)
        if product:
            order = Order(
                date_ordered = date.today(),
                user_id = get_jwt_identity(),
                product = product,
                quantity = body_data.get('quantity'),
                status = 'In-queue',
                delivery_pup_date = datetime.strptime(body_data.get('delivery_pup_date'),'%d/%m/%Y')
            )
            
            db.session.add(order)
            db.session.commit()
            return order_schema.dump(order), 201
        else:
            return {'error': f'Product not found with id {product_id}.'}, 404
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {'error': f'{err.orig.diag.column_name} is required to order a product.'}, 409


@orders_bp.route('/<int:id>', methods = ['PUT','PATCH'])
@jwt_required()
def edit_order(id):
    body_data = request.get_json()
    qry = db.select(Order).where(Order.id == id)
    order = db.session.scalar(qry)
    if order:
        order.quantity = body_data.get('quantity') or order.message
        order.status = body_data.get('status') or order.status
        order.delivery_pup_date = body_data.get('delivery_pup_date') or order.delivery_pup_date
        db.session.commit()
        return order_schema.dump(order)
    else:
        return {'error': f'Order with id:{id} not found.'}

# NEEDS user who ordered or IS_ADMIN TO DELETE!!!!
@orders_bp.route('/<int:id>', methods = ['DELETE'])
def delete_order(id):
    qry = db.select(Order).where(Order.id == id)
    order = db.session.scalar(qry)
    if order:
        db.session.delete(order)
        db.session.commit()
        return {'message': f"Order {id} deleted successfully."}
    else:
        return {'error': f'Order with id {id} not found'}

