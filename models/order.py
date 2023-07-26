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

    @validates('product_id')
    def is_product(self, value):
        qry = db.select(Product).filter_by(id = value)
        product = db.session.scalar(qry)
        if not product:
            raise ValidationError(f'Product not found with id:{value}.')

    status = fields.String(validate = OneOf(VALID_STATUSES))

    quantity = fields.Integer(required = True, validate = Range(min=1, max=1, error = "Can only order 1 of this Product."))

    @validates('delivery_pup_date')
    def validate_delpup_to_prep(self, value):
        date_ordered = date.today()
        todays_date = datetime.strftime(date_ordered, '%Y-%m-%d')
        delpup_date = datetime.strptime(value, '%d/%m/%Y').strftime('%Y-%m-%d')
        if delpup_date < todays_date:
            raise ValidationError('Date cannot be in the past.')
        body_data = request.get_json()
        product_id = body_data.get('product_id')
        qry = db.select(Product.prep_days).filter_by(id = product_id)
        if product_id == None:
            raise ValidationError('Please enter the product id you wish to edit.')
        prep_days = db.session.scalar(qry)
        available = date_ordered + timedelta(days = (prep_days + 1))
        date_available = datetime.strftime(available, '%Y-%m-%d')
        if delpup_date < date_available:
            raise ValidationError(f'Order will not be ready by this date, please enter a date at least {prep_days + 1} days from today.')

    class Meta:
        fields = ('id', 'user_id', 'date_ordered', 'product_id', 'quantity', 'status', 'description', 'delivery_pup_date')
        ordered = True

order_schema = OrderSchema()
orders_schema = OrderSchema(many = True)