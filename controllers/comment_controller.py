from flask import Blueprint, request
from init import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.product import Product 
from models.comment import Comment, comment_schema
from models.user import User


comments_bp = Blueprint('comments', __name__, url_prefix = '/<int:product_id>/comments')


@comments_bp.route('/', methods = ['POST'])
# JSON Web Token required from login to use this method
@jwt_required()
def create_comment(product_id):
    # retrieve JSON data parsed into the body from the front end as a python object and store it in body_data
    body_data = request.get_json()
    # Query the database to find the product id parsed as the arguement of the fuction in the products table
    qry = db.select(Product).filter_by(id = product_id)
    # stores the query in product variable
    product = db.session.scalar(qry)
    # If the product id is found in the database the comment will be added to that product
    if product:
        comment = Comment(
            message = body_data.get('message'),
            # links the users web token granted from login credentials in the database
            user_id = get_jwt_identity(),
            product = product
        )
        db.session.add(comment)
        # Commit the added comment to the database
        db.session.commit()
        # Return the contents 
        return comment_schema.dump(comment), 201
    # If the product id is not found in the database an error message will be returned
    else:
        return {'error': f'Product not found with id {product_id}.'}, 404
        

# No GET method for comments, all comments will exist and be related to products, so any GET product will display comments 


@comments_bp.route('/<int:comment_id>', methods = ['DELETE'])
# JSON Web Token required from login to use this method
@jwt_required()
def delete_comment(comment_id):
    # Checks to see if the user trying to post a product has is_admin attribute in the database
    is_admin = authorise_as_admin()
    # Query the database to find the comment id parsed as the arguement of the fuction in the comments table
    qry = db.select(Comment).filter_by(id = comment_id)
    # stores the query in comment variable
    comment = db.session.scalar(qry)
    # If the comment id is found in the database the comment can be deleted
    if comment:
        # Checks if user trying to delete is an admin
        if is_admin:
            db.session.delete(comment)
            db.session.commit()
            return {'message': f'Comment "{comment.message}" has been deleted successfully.'}, 200
        # Checks the database to see if the user id trying to delete the comment matches the user that posted the comment
        # If not return error message, otherwise the user id matches and the comment is deleted
        if str(comment.user_id) != get_jwt_identity():
            return {'error': 'Only the user this comment belongs to can delete it.'}, 401
        db.session.delete(comment)
        db.session.commit()
        return {'message': f'Comment "{comment.message}" has been deleted successfully.'}, 200
    # If the comment id is not found in the database return an error message
    else: 
        return {'error': f'Comment with id {comment_id} not found.'}, 404
    

@comments_bp.route('/<int:comment_id>', methods = ['PUT', 'PATCH'])
# JSON Web Token required from login to use this method
@jwt_required()
def edit_comment(comment_id):
    # retrieve JSON data parsed into the body from the front end as a python object and store it in body_data
    body_data = request.get_json()
    # Query the database to find the comment id parsed as the arguement of the fuction in the comments table
    qry = db.select(Comment).filter_by(id = comment_id)
    # stores the query in comment variable
    comment = db.session.scalar(qry)
     # If the comment id is found in the database the comment can be edited
    if comment:
        # Checks the database to see if the user id trying to edit the comment matches the user that posted the comment
        # If not return error message, otherwise the user id matches and the comment is edited
        if str(comment.user_id) != get_jwt_identity():
            return {'error': 'Only the user this comment belongs to can edit it.'}, 401
        comment.message = body_data.get('message') or comment.message
        db.session.commit()
        return comment_schema.dump(comment)
    # If the comment id is not found in the database return an error message
    else:
        return {'error': f'Comment with id {comment_id} not found.'}, 404
    

def authorise_as_admin():
    # Check web token to get the user associated to that token
    user_id = get_jwt_identity()
    # Query the database to find the user id detected by the web token in the users table 
    # if the user has is_admin set as True then return that the user is admin
    qry = db.select(User).filter_by(id = user_id)
    user = db.session.scalar(qry)
    return user.is_admin