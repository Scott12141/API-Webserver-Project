from init import db, ma 
from marshmallow import fields

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.Text, nullable = False)
    price = db.Column(db.Float, default = 0.00)
    prep_days = db.Column(db.Integer, nullable = False)
    
    comments = db.relationship('Comment', back_populates = 'product', cascade = 'all, delete')
    orders = db.relationship('Order', back_populates = 'product', cascade = 'all, delete')

class ProductSchema(ma.Schema):

    comments = fields.List(fields.Nested('CommentSchema'), exclude = ['product'])
    orders = fields.List(fields.Nested('OrderSchema'), exclude = ['product'])

    class Meta:
        fields = ('id', 'name', 'description', 'price', 'prep_days','comments', 'orders')
        ordered = True

product_schema = ProductSchema()
products_schema = ProductSchema(many = True)