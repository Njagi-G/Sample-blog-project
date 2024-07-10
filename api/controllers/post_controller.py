from flask import Blueprint, request, jsonify
from models import Post, db
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from datetime import datetime, timedelta
from utils import error_handler

post_routes = Blueprint('post_routes', __name__, url_prefix='/api/post')

@post_routes.route('/create', methods=['POST'])
@jwt_required()
def create_post():
    try:
        title = request.json.get('title')
        content = request.json.get('content')
        category = request.json.get('category', 'uncategorized')
        image = request.json.get('image', 'https://www.hostinger.com/tutorials/wp-content/uploads/sites/2/2021/09/how-to-write-a-blog-post.png')
        user_id = get_jwt_identity()

        if not title or not content:
            return error_handler(400, 'Please provide all required fields')

        new_post = Post(title=title, content=content, category=category, image=image, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        return jsonify(new_post.to_dict()), 201
    except Exception as e:
        return error_handler(500, str(e))

@post_routes.route('/getposts', methods=['GET'])
def get_posts():
    try:
        start_index = int(request.args.get('startIndex', 0))
        limit = int(request.args.get('limit', 9))
        sort_direction = 'desc' if request.args.get('order') == 'desc' else 'asc'

        query = Post.query
        if request.args.get('userId'):
            query = query.filter_by(user_id=request.args.get('userId'))
        if request.args.get('category'):
            query = query.filter_by(category=request.args.get('category'))
        if request.args.get('postId'):
            query = query.filter_by(id=request.args.get('postId'))
        if request.args.get('searchTerm'):
            search_term = request.args.get('searchTerm')
            query = query.filter(Post.title.ilike(f'%{search_term}%') | Post.content.ilike(f'%{search_term}%'))

        posts = query.order_by(getattr(Post, request.args.get('sortBy', 'created_at')).desc() if sort_direction == 'desc' else getattr(Post, request.args.get('sortBy', 'created_at')).asc()).slice(start_index, start_index + limit).all()
        total_posts = query.count()

        now = datetime.utcnow()
        one_month_ago = now - timedelta(days=30)
        last_month_posts = Post.query.filter(Post.created_at >= one_month_ago).count()

        return jsonify({
            'posts': [post.to_dict() for post in posts],
            'totalPosts': total_posts,
            'lastMonthPosts': last_month_posts
        }), 200
    except Exception as e:
        return error_handler(500, str(e))

@post_routes.route('/deletepost/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    try:
        post = Post.query.get(post_id)
        if not post:
            return error_handler(404, 'Post not found')

        user_id = get_jwt_identity()
        if post.user_id != user_id and not get_jwt_claims()['isAdmin']:
            return error_handler(403, 'You are not allowed to delete this post')

        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'The post has been deleted'}), 200
    except Exception as e:
        return error_handler(500, str(e))

@post_routes.route('/updatepost/<post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    try:
        post = Post.query.get(post_id)
        if not post:
            return error_handler(404, 'Post not found')

        user_id = get_jwt_identity()
        if post.user_id != user_id and not get_jwt_claims()['isAdmin']:
            return error_handler(403, 'You are not allowed to update this post')

        post.title = request.json.get('title', post.title)
        post.content = request.json.get('content', post.content)
        post.category = request.json.get('category', post.category)
        post.image = request.json.get('image', post.image)

        db.session.commit()
        return jsonify(post.to_dict()), 200
    except Exception as e:
        return error_handler(500, str(e))