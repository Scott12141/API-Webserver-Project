from init import db, jwt
from flask import Blueprint, request
from models.order import Order, order_schema, orders_schema
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2 import errorcodes
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import date, datetime
from models.user import User


orders_bp = Blueprint('orders', __name__, url_prefix = '/orders')


@orders_bp.route('/')
# JSON Web Token required from login to use this method
@jwt_required()
def get_orders():
    # Checks to see if the user trying to read orders has is_admin attribute in the database
    is_admin = authorise_as_admin()
    if is_admin:
        # If the user is an admin queries the database to retrieve and display all orders with no filter
        qry = db.select(Order)
        orders = db.session.scalars(qry)
        return orders_schema.dump(orders)
    else:
        # If the user is not an admin it will 
        # query the database to retrieve and display only orders that match the user id of the user conducting the query
        user_id = get_jwt_identity()
        qry = db.select(Order).where(Order.user_id == user_id)
        user_orders = db.session.scalars(qry)
        return orders_schema.dump(user_orders)


@orders_bp.route('/<int:id>')
# JSON Web Token required from login to use this method
@jwt_required()
def get_one_order(id):
    # Checks to see if the user trying to read orders has is_admin attribute in the database
    is_admin = authorise_as_admin()
    # queries the database in the orders table where the order id is equal to id passed into the function as the argument
    qry = db.select(Order).where(Order.id == id)
    order = db.session.scalar(qry)
    # If the order id is found in the database 
    # the product will be displayed to the user so long as they are eiher an admin or the user that created the order
    if order:
        if is_admin or str(order.user_id) == get_jwt_identity():
            return order_schema.dump(order)
        # if they are not an admin or the user that created the order they will recieve an error message
        else:
            return {'error': 'Only the user this order belongs to can veiw it.'}, 401
    # If an order by that id does not exist then return an error message
    else:
        return {'error': f'Order with id {id} not found.'}, 404

@orders_bp.route('/', methods = ['POST'])
# JSON Web Token required from login to use this method
@jwt_required()
def create_order():
    try:
        # retrieve JSON data parsed into the body from the front end as a python object and store it in body_data
        # load product schema for validation of partially parsed data 
        body_data = order_schema.load(request.get_json())
        order = Order(
            date_ordered = date.today(),
            # links the users web token granted from login credentials in the database
            user_id = get_jwt_identity(),
            product_id = body_data.get('product_id'),
            quantity = body_data.get('quantity'),
            status = 'In-queue',
            description = body_data.get('description'),
            # get the user to enter their desired delivery/pick-up date in DD/MM/YYYY format (Local format)
            delivery_pup_date = datetime.strptime(body_data.get('delivery_pup_date'),'%d/%m/%Y')
        )
        # Commit added order to the database
        db.session.add(order)
        db.session.commit()
        # Returns the order data to the user in JSON format 
        return order_schema.dump(order), 201
    # Validates not null, data type and value constraints
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {'error': f'{err.orig.diag.column_name} is required to order a product.'}, 409
    except ValueError as err:
        if err:
            return {'error': 'Date needs to be in DD/MM/YYYY format.'}, 409
    except DataError as err:
        if err.orig.pgcode == errorcodes.INVALID_TEXT_REPRESENTATION:
            return {'error': 'Please enter product_id as a number.'}, 409


@orders_bp.route('/<int:id>', methods = ['PUT','PATCH'])
# JSON Web Token required from login to use this method
@jwt_required()
def edit_order(id):
    try:
        # Checks to see if the user trying to read orders has is_admin attribute in the database
        is_admin = authorise_as_admin()
        # retrieve JSON data parsed into the body from the front end as a python object and store it in body_data
        # load product schema for validation of partially parsed data 
        body_data = order_schema.load(request.get_json(), partial = True)
        # queries the database in the orders table where the order id is equal to id passed into the function as the argument
        qry = db.select(Order).where(Order.id == id)
        # stores the query in order variable
        order = db.session.scalar(qry)
        # If the order id is found in the database continue
        if order:
            # If the current status of the order is either Preparing or Completed then its too late to edit the order and return error message
            if order.status in ['Preparing', 'Completed']:
                return {'error': 'This order has already began preparation or has been completed and can no longer be edited.'}, 403
            # Only an admin or the user the order belongs too can edit it
            if is_admin or str(order.user_id) == get_jwt_identity():
                order.product_id = body_data.get('product_id') or order.product_id
                order.status = body_data.get('status') or order.status
                order.description = body_data.get('description') or order.description
                # Formats the delivery/pick-up date back to a string so that if a new date isnt parsed it can parse the previous date
                order.delivery_pup_date = datetime.strftime(order.delivery_pup_date, '%d/%m/%Y')
                order.delivery_pup_date = datetime.strptime(body_data.get('delivery_pup_date') or order.delivery_pup_date ,'%d/%m/%Y')
                # Commits the updates to the order
                db.session.commit()
                # Return the altered order schema for the order matching the id 
                return order_schema.dump(order)
            # If the user id doesnt match the user id that created the order or have is_admin then return error message
            else:
                return {'error': 'Only the user this order belongs to can edit it.'}, 401
        # If an order by that id does not exist then return an error message    
        else:
            return {'error': f'Order with id:{id} not found.'}, 404
    # Validates value constraints    
    except ValueError as err:
        if err:
            return {'error': 'Date needs to be in DD/MM/YYYY format.'}, 409



@orders_bp.route('/<int:id>', methods = ['DELETE'])
# JSON Web Token required from login to use this method
@jwt_required()
def delete_order(id):
    # Checks to see if the user trying to read orders has is_admin attribute in the database
    is_admin = authorise_as_admin()
    # queries the database in the orders table where the order id is equal to id passed into the function as the argument
    qry = db.select(Order).where(Order.id == id)
    # stores the query in order variable
    order = db.session.scalar(qry)
    # If the order id is found in the database continue
    if order:
        # Only an admin or the user the order belongs too can delete it
        if is_admin or str(order.user_id) == get_jwt_identity():
            db.session.delete(order)
            # Commits the order deletion to the database
            db.session.commit()
            return {'message': f"Order {id} deleted successfully."}, 200
        # If the user id doesnt match the user id that created the order or have is_admin then return error message
        else:
            return {'error': 'Only the user this order belongs to can delete it.'}, 401 
    # If an order by that id does not exist then return an error message     
    else:
        return {'error': f'Order with id {id} not found'}, 404


def authorise_as_admin():
    # Check web token to get the user associated to that token
    user_id = get_jwt_identity()
    # Query the database to find the user id detected by the web token in the users table 
    # if the user has is_admin set as True then return that the user is admin
    qry = db.select(User).filter_by(id = user_id)
    user = db.session.scalar(qry)
    return user.is_admin