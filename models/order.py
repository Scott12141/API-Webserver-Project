from init import db, ma
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import OneOf, Range
from datetime import date, datetime, timedelta
from models.product import Product
from flask import request

VALID_STATUSES = ('In-queue', 'Preparing', 'Completed')

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key = True)
    date_ordered = db.Column(db.Date)
    quantity = db.Column(db.Integer, nullable = False)
    status = db.Column(db.String, default = 'In-queue')
    description = db.Column(db.Text, nullable = False)
    delivery_pup_date = db.Column(db.Date, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable = False)

    user = db.relationship('User', back_populates = 'orders')
    product = db.relationship('Product', back_populates = 'orders')

class OrderSchema(ma.Schema):
    user = fields.Nested('UserSchema', only = ['first_name', 'last_name', 'address'])
    product = fields.Nested('ProductSchema', exclude = ['comments'])

    # Validates that a product id has been entered for ordering
    @validates('product_id')
    def is_product(self, value):
        # Query the database to find the product id parsed as the arguement of the fuction in the products table
        qry = db.select(Product).filter_by(id = value)
        product = db.session.scalar(qry)
        # If the product id is not found in the database an error message will be returned
        if not product:
            raise ValidationError(f'Product not found with id:{value}.')

    # Validates that the status field can only have one of the three statuses defined in VALID_STATUSES
    status = fields.String(validate = OneOf(VALID_STATUSES))
    # Validates that the quantity ordered cannot be more than 1, 
    # if for some reason a user would want more than one wedding or celebration cake, they can place multiple orders
    # if they want more cupcakes the products are sold in 6, 12, 18 etc. quantities with varying price points
    quantity = fields.Integer(required = True, validate = Range(min=1, max=1, error = "Can only order 1 of this Product."))

    @validates('delivery_pup_date')
    def validate_delpup_to_prep(self, value):
        # sets date ordered as date order was placed
        date_ordered = date.today()
        # formats date ordered so it can be used in a comparison 
        todays_date = datetime.strftime(date_ordered, '%Y-%m-%d')
        # takes the value entered from the JSON request in a DD/MM/YYYY format
        # then formats it so it can be used in a comparison 
        delpup_date = datetime.strptime(value, '%d/%m/%Y').strftime('%Y-%m-%d')
        # checks to see if the delivery/pick-up date entered comes before the date ordered
        if delpup_date < todays_date:
            # if the delivery/pick-up date entered comes before the date ordered then raise an error and return message
            raise ValidationError('Date cannot be in the past.')
        # retrieve JSON data parsed into the posted order body from the front end as a python object and store it in body_data
        body_data = request.get_json()
        # find the id of the product being ordered
        product_id = body_data.get('product_id')
        # Query the database to find the preparation days attribute of the product being ordered from its id parsed into the body
        qry = db.select(Product.prep_days).filter_by(id = product_id)
        prep_days = db.session.scalar(qry)
        # Validates that a product id has been entered for ordering and raises error if not
        if product_id == None:
            raise ValidationError('Please enter the product id you wish to edit.')
        # sets the date that an order will be available for delivery/pick-up
        # by adding the preparation days + 1 to the date the order was placed
        available = date_ordered + timedelta(days = (prep_days + 1))
        # formats date available so it can be used in a comparison 
        date_available = datetime.strftime(available, '%Y-%m-%d')
        # checks to see if the date entered in the body is too early for delivery/pick-up and raises an error message if it is
        if delpup_date < date_available:
            raise ValidationError(f'Order will not be ready by this date, please enter a date at least {prep_days + 1} days from today.')

    class Meta:
        fields = ('id', 'user_id', 'date_ordered', 'product_id', 'quantity', 'status', 'description', 'delivery_pup_date')
        ordered = True

order_schema = OrderSchema()
orders_schema = OrderSchema(many = True)