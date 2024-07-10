from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.controllers.post_controller import create_post, get_posts, delete_post, update_post

post_routes = Blueprint('post_routes', __name__, url_prefix='/api/post')

@post_routes.route('/create', methods=['POST'])
@jwt_required()
def create():
    user_id = get_jwt_identity()
    if not user_id['isAdmin']:
        return {'error': 'You are not allowed to create a post'}, 403

    title = request.json.get('title')
    content = request.json.get('content')

    if not title or not content:
        return {'error': 'Please provide all required fields'}, 400

    return create_post(user_id, title, content)

@post_routes.route('/getposts', methods=['GET'])
def get_posts():
    return get_posts(request.args)

@post_routes.route('/deletepost/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = get_jwt_identity()
    if not user_id['isAdmin']:
        return {'error': 'You are not allowed to delete this post'}, 403

    return delete_post(post_id, user_id)

@post_routes.route('/updatepost/<post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    user_id = get_jwt_identity()
    if not user_id['isAdmin']:
        return {'error': 'You are not allowed to update this post'}, 403

    title = request.json.get('title')
    content = request.json.get('content')
    category = request.json.get('category')
    image = request.json.get('image')

    return update_post(post_id, user_id, title, content, category, image)
