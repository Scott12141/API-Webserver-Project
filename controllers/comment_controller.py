from flask import Blueprint, request
from init import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.product import Product 
from models.comment import Comment, comment_schema
from models.user import User



comments_bp = Blueprint('comments', __name__, url_prefix = '/<int:product_id>/comments')


@comments_bp.route('/', methods = ['POST'])
@jwt_required()
def create_comment(product_id):
    body_data = request.get_json()
    qry = db.select(Product).filter_by(id = product_id) 
    product = db.session.scalar(qry)
    if product:
        comment = Comment(
            message = body_data.get('message'),
            user_id = get_jwt_identity(),
            product = product
        )
        db.session.add(comment)
        db.session.commit()
        return comment_schema.dump(comment), 201
    else:
        return {'error': f'Product not found with id {product_id}.'}, 404
        

# No GET method for comments, all comments will exist and be related to products, so any GET product will display comments 


@comments_bp.route('/<int:comment_id>', methods = ['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    is_admin = authorise_as_admin()
    qry = db.select(Comment).filter_by(id = comment_id)
    comment = db.session.scalar(qry)
    if comment:
        if is_admin:
            db.session.delete(comment)
            db.session.commit()
            return {'message': f'Comment "{comment.message}" has been deleted successfully.'}
        if str(comment.user_id) != get_jwt_identity():
            return {'error': 'Only the user this comment belongs to can delete it.'}
        db.session.delete(comment)
        db.session.commit()
        return {'message': f'Comment "{comment.message}" has been deleted successfully.'}
    else: 
        return {'error': f'Comment with id {comment_id} not found.'}, 404
    

@comments_bp.route('/<int:comment_id>', methods = ['PUT', 'PATCH'])
@jwt_required()
def edit_comment(comment_id):
    body_data = request.get_json()
    qry = db.select(Comment).filter_by(id = comment_id)
    comment = db.session.scalar(qry)
    if comment:
        if str(comment.user_id) != get_jwt_identity():
            return {'error': 'Only the user this comment belongs to can edit it.'}
        comment.message = body_data.get('message') or comment.message
        db.session.commit()
        return comment_schema.dump(comment)
    else:
        return {'error': f'Comment with id {comment_id} not found.'}
    

def authorise_as_admin():
    user_id = get_jwt_identity()
    qry = db.select(User).filter_by(id = user_id)
    user = db.session.scalar(qry)
    return user.is_admin