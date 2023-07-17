from init import db, ma
from marshmallow import fields

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


class UserSchema(ma.Schema):

    comments = fields.List(fields.Nested('CommentSchema', exclude = ['user']))

    class Meta:
        fields = ('id', 'first_name', 'last_name', 'address', 'email', 'password', 'is_admin', 'comments')
        ordered = True

user_schema = UserSchema(exclude=['password'])
users_schema = UserSchema(many=True, exclude=['password'])
    