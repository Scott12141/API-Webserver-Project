from init import db, ma
from marshmallow import fields


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key = True)
    date_ordered = db.Column(db.Date)
    quantity = db.Column(db.Integer)
    status = db.Column(db.String)
    delivery_pup_date = db.Column(db.Date)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable = False)

    user = db.relationship('User', back_populates = 'orders')
    product = db.relationship('Product', back_populates = 'orders')

class OrderSchema(ma.Schema):
    user = fields.Nested('UserSchema', only = ['first_name', 'last_name', 'address'])
    product = fields.Nested('ProductSchema', exclude = ['comments'])

    class Meta:
        fields = ('id', 'date_ordered', 'quantity', 'status', 'delivery_pup_date')
        ordered = True

order_schema = OrderSchema()
orders_schema = OrderSchema(many = True)