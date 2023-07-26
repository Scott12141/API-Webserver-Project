from init import db, jwt
from flask import Blueprint, request
from models.order import Order, order_schema, orders_schema
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import date, datetime
from models.user import User


orders_bp = Blueprint('orders', __name__, url_prefix = '/orders')


@orders_bp.route('/')
@jwt_required()
def get_orders():
    # queries the database to retrieve and display all orders with no filter
    is_admin = authorise_as_admin()
    if is_admin:
        qry = db.select(Order)
        orders = db.session.scalars(qry)
        return orders_schema.dump(orders)
    else:
        user_id = get_jwt_identity()
        qry = db.select(Order).where(Order.user_id == user_id)
        user_orders = db.session.scalars(qry)
        return orders_schema.dump(user_orders)


@orders_bp.route('/<int:id>')
@jwt_required()
def get_one_order(id):
    # queries the database in the orders table where the order id is equal to whatever id is passed into the front end as the argument
    is_admin = authorise_as_admin()
    qry = db.select(Order).where(Order.id == id)
    order = db.session.scalar(qry)
    if order:
        if is_admin or str(order.user_id) == get_jwt_identity():
            return order_schema.dump(order)
        else:
            return {'error': 'Only the user this order belongs to can veiw it.'}  
    else:
        return {'error': f'Order with id {id} not found.'}, 404

@orders_bp.route('/', methods = ['POST'])
@jwt_required()
def create_order():
    try:
        body_data = order_schema.load(request.get_json())
        order = Order(
            date_ordered = date.today(),
            user_id = get_jwt_identity(),
            product_id = body_data.get('product_id'),
            quantity = body_data.get('quantity'),
            status = 'In-queue',
            description = body_data.get('description'),
            delivery_pup_date = datetime.strptime(body_data.get('delivery_pup_date'),'%d/%m/%Y')
        )
        db.session.add(order)
        db.session.commit()
        return order_schema.dump(order), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {'error': f'{err.orig.diag.column_name} is required to order a product.'}, 409
    except ValueError as err:
        if err:
            return {'error': 'Date needs to be in DD/MM/YYYY format.'}, 409


@orders_bp.route('/<int:id>', methods = ['PUT','PATCH'])
@jwt_required()
def edit_order(id):
    try:
        is_admin = authorise_as_admin()
        body_data = order_schema.load(request.get_json(), partial = True)
        qry = db.select(Order).where(Order.id == id)
        order = db.session.scalar(qry)
        if order:
            if order.status in ['Preparing', 'Completed']:
                return {'error': 'This order has already began preparation or has been completed and can no longer be edited.'}
            if is_admin or str(order.user_id) == get_jwt_identity():
                order.product_id = body_data.get('product_id') or order.product_id
                order.status = body_data.get('status') or order.status
                order.description = body_data.get('description') or order.description
                order.delivery_pup_date = datetime.strftime(order.delivery_pup_date, '%d/%m/%Y')
                order.delivery_pup_date = datetime.strptime(body_data.get('delivery_pup_date') or order.delivery_pup_date ,'%d/%m/%Y')
                db.session.commit()
                return order_schema.dump(order)
            else:
                return {'error': 'Only the user this order belongs to can edit it.'}
        else:
            return {'error': f'Order with id:{id} not found.'}
    except ValueError as err:
        if err:
            return {'error': 'Date needs to be in DD/MM/YYYY format.'}, 409



@orders_bp.route('/<int:id>', methods = ['DELETE'])
@jwt_required()
def delete_order(id):
    is_admin = authorise_as_admin()
    qry = db.select(Order).where(Order.id == id)
    order = db.session.scalar(qry)
    if order:  
        if is_admin or str(order.user_id) == get_jwt_identity():
            db.session.delete(order)
            db.session.commit()
            return {'message': f"Order {id} deleted successfully."}
        else:
            return {'error': 'Only the user this order belongs to can delete it.'}    
    else:
        return {'error': f'Order with id {id} not found'}


def authorise_as_admin():
    user_id = get_jwt_identity()
    qry = db.select(User).filter_by(id = user_id)
    user = db.session.scalar(qry)
    return user.is_admin