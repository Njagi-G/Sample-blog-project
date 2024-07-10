from flask import Blueprint, request, jsonify
from models import Comment, db
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from datetime import datetime, timedelta
from utils import error_handler

comment_routes = Blueprint('comment_routes', __name__)

@comment_routes.route('/create', methods=['POST'])
@jwt_required()
def create_comment():
    try:
        content = request.json.get('content')
        post_id = request.json.get('postId')
        user_id = get_jwt_identity()

        if not content or not post_id:
            return error_handler(400, 'Please provide all required fields')

        new_comment = Comment(content=content, post_id=post_id, user_id=user_id)
        db.session.add(new_comment)
        db.session.commit()

        return jsonify(new_comment.to_dict()), 200
    except Exception as e:
        return error_handler(500, str(e))

@comment_routes.route('/getPostComments/<int:post_id>', methods=['GET'])
def get_post_comments(post_id):
    try:
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
        return jsonify([comment.to_dict() for comment in comments]), 200
    except Exception as e:
        return error_handler(500, str(e))

@comment_routes.route('/likeComment/<int:comment_id>', methods=['PUT'])
@jwt_required()
def like_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return error_handler(404, 'Comment not found')

        user_id = get_jwt_identity()
        if user_id in comment.likes:
            comment.number_of_likes -= 1
            comment.likes.remove(user_id)
        else:
            comment.number_of_likes += 1
            comment.likes.append(user_id)

        db.session.commit()
        return jsonify(comment.to_dict()), 200
    except Exception as e:
        return error_handler(500, str(e))

@comment_routes.route('/editComment/<int:comment_id>', methods=['PUT'])
@jwt_required()
def edit_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return error_handler(404, 'Comment not found')

        user_id = get_jwt_identity()
        claims = get_jwt_claims()
        if comment.user_id != user_id and not claims.get('isAdmin', False):
            return error_handler(403, 'You are not allowed to edit this comment')

        comment.content = request.json.get('content')
        db.session.commit()
        return jsonify(comment.to_dict()), 200
    except Exception as e:
        return error_handler(500, str(e))

@comment_routes.route('/deleteComment/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return error_handler(404, 'Comment not found')

        user_id = get_jwt_identity()
        claims = get_jwt_claims()
        if comment.user_id != user_id and not claims.get('isAdmin', False):
            return error_handler(403, 'You are not allowed to delete this comment')

        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment has been deleted'}), 200
    except Exception as e:
        return error_handler(500, str(e))

@comment_routes.route('/getcomments', methods=['GET'])
@jwt_required()
def get_comments():
    try:
        claims = get_jwt_claims()
        if not claims.get('isAdmin', False):
            return error_handler(403, 'You are not allowed to get all comments')

        start_index = int(request.args.get('startIndex', 0))
        limit = int(request.args.get('limit', 9))
        sort_direction = -1 if request.args.get('sort') == 'desc' else 1

        comments = Comment.query.order_by(Comment.created_at.desc() if sort_direction == -1 else Comment.created_at.asc()).slice(start_index, start_index + limit).all()
        total_comments = Comment.query.count()

        now = datetime.utcnow()
        one_month_ago = now - timedelta(days=30)
        last_month_comments = Comment.query.filter(Comment.created_at >= one_month_ago).count()

        return jsonify({
            'comments': [comment.to_dict() for comment in comments],
            'totalComments': total_comments,
            'lastMonthComments': last_month_comments
        }), 200
    except Exception as e:
        return error_handler(500, str(e))
