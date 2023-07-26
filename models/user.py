from init import db, ma
from marshmallow import fields
from marshmallow.validate import Length, And, Regexp

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    comments = db.relationship('Comment', back_populates = 'user')
    orders = db.relationship('Order', back_populates = 'user')

class UserSchema(ma.Schema):

    comments = fields.List(fields.Nested('CommentSchema', exclude = ['user']))
    orders = fields.List(fields.Nested('OrderSchema', exclude = ['user']))

    password = fields.String(required = True, validate = And(
        Length(min = 5, max = 16, error = 'Password must be between 5 and 16 characters long.'),
        Regexp('^[a-zA-Z0-9]+$', error = 'Only letters and numbers can be used for the password.')
    ))

    class Meta:
        fields = ('id', 'first_name', 'last_name', 'address', 'email', 'password', 'is_admin', 'comments', 'orders')
        ordered = True

user_schema = UserSchema()# cant use exclude=['password'], if we exclude the password in the shcema then password validation cant be used.
users_schema = UserSchema(many=True, exclude=['password'])
    