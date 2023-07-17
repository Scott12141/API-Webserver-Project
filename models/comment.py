from init import db, ma
from marshmallow import fields


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key = True)
    message = db.Column(db.Text,)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable = False)

    user = db.relationship('User', back_populates = 'comments')
    product = db.relationship('Product', back_populates = 'comments')

class CommentSchema(ma.Schema):
    user = fields.Nested('UserSchema', only = ['first_name', 'last_name'])
    product = fields.Nested('ProductSchema', exclude = ['comments'])

    class Meta:
        fields = ('id', 'message', 'user', 'product')


comment_schema = CommentSchema()
comments_schema = CommentSchema(many = True)