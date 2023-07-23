from init import db, ma
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import OneOf, Range
from datetime import date, datetime
from models.product import Product

VALID_STATUSES = ('In-queue', 'Preparing', 'Completed')

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key = True)
    date_ordered = db.Column(db.Date)
    quantity = db.Column(db.Integer, nullable = False)
    status = db.Column(db.String, default = 'In-queue')
    delivery_pup_date = db.Column(db.Date, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable = False)

    user = db.relationship('User', back_populates = 'orders')
    product = db.relationship('Product', back_populates = 'orders')

class OrderSchema(ma.Schema):
    user = fields.Nested('UserSchema', only = ['first_name', 'last_name', 'address'])
    product = fields.Nested('ProductSchema', exclude = ['comments'])

    status = fields.String(validate = OneOf(VALID_STATUSES))

    quantity = fields.Integer(required = True, validate = Range(min=1, max=1, error = "Can only order 1 of this Product."))

    @validates('delivery_pup_date')
    def validate_delpup_to_prep(self, value): #product_id, 
        # qry = db.select(Product).filter_by(id = product_id).select(Product.prep_days)
        # prep_days = db.session.scalar(qry)
        date_ordered = date.today()
        todays_date = datetime.strftime(date_ordered, '%Y-%m-%d')
        new_value = datetime.strptime(value, '%d/%m/%Y').strftime('%Y-%m-%d')
        if new_value < todays_date:
            raise ValidationError('Date cannot be in the past.')


    class Meta:
        fields = ('id', 'user_id', 'date_ordered', 'product_id', 'quantity', 'status', 'delivery_pup_date')
        ordered = True

order_schema = OrderSchema()
orders_schema = OrderSchema(many = True)