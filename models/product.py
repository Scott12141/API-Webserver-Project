from init import db, ma 
from marshmallow import fields
from marshmallow.validate import Range, Length

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False, unique = True)
    description = db.Column(db.Text, nullable = False)
    price = db.Column(db.Float, nullable = False)
    prep_days = db.Column(db.Integer, nullable = False)
    
    comments = db.relationship('Comment', back_populates = 'product', cascade = 'all, delete')
    orders = db.relationship('Order', back_populates = 'product', cascade = 'all, delete')

class ProductSchema(ma.Schema):

    comments = fields.List(fields.Nested('CommentSchema'), exclude = ['product'])
    orders = fields.List(fields.Nested('OrderSchema'), exclude = ['product'])

    # Validates that the name of the product is at least 4 letters long
    name = fields.String(required = True, validate = Length(min = 4, error = 'Product name must be at least the length of cake.'))
    # Validates that the price of the product can only be set in the range of $15 and $500 
    price = fields.Float(required = True, validate = Range(min = 15, max = 500, error = "Price must be in the range of $15 to $500."))
    # Validates that the a product can only take a maximum of 5 days to prepare
    prep_days = fields.Integer(required = True, validate = Range(max = 5, error = 'Preperation days cannot be longer than 5'))

    class Meta:
        fields = ('id', 'name', 'description', 'price', 'prep_days','comments', 'orders')
        ordered = True

product_schema = ProductSchema()
products_schema = ProductSchema(many = True)