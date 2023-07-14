from init import db, ma 

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.Text, nullable = False)
    price = db.Column(db.Float, default = 0.00)
    preparation_time = db.Column(db.String, nullable = False)
    

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'price', 'preparation_time')
        ordered = True

product_schema = ProductSchema()
products_schema = ProductSchema(many = True)