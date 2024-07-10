from flask import Blueprint, request, jsonify
from functools import wraps
from models import Comment
from utils import verify_token, error_handler
from datetime import datetime, timedelta

comment_routes = Blueprint('comment_routes', __name__)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            user_data = verify_token(token)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        return func(user_data, *args, **kwargs)
    return decorated

@comment_routes.route('/create', methods=['POST'])
@token_required
def create_comment(user_data):
    content = request.json.get('content')
    post_id = request.json.get('postId')
    user_id = user_data.get('id')

    if user_id != user_data.get('id'):
        return error_handler(403, 'You are not allowed to create this comment')

    new_comment = Comment(content=content, post_id=post_id, user_id=user_id)
    new_comment.save()

    return jsonify(new_comment.to_dict()), 200

@comment_routes.route('/getPostComments/<post_id>', methods=['GET'])
def get_post_comments(post_id):
    comments = Comment.objects(post_id=post_id).order_by('-created_at')
    return jsonify([comment.to_dict() for comment in comments]), 200

@comment_routes.route('/likeComment/<comment_id>', methods=['PUT'])
@token_required
def like_comment(user_data, comment_id):
    comment = Comment.objects.get_or_404(id=comment_id)
    user_id = user_data.get('id')

    if user_id in comment.likes:
        comment.update(dec__number_of_likes=1, pull__likes=user_id)
    else:
        comment.update(inc__number_of_likes=1, push__likes=user_id)

    return jsonify(comment.to_dict()), 200

@comment_routes.route('/editComment/<comment_id>', methods=['PUT'])
@token_required
def edit_comment(user_data, comment_id):
    comment = Comment.objects.get_or_404(id=comment_id)
    user_id = user_data.get('id')
    is_admin = user_data.get('isAdmin')

    if comment.user_id != user_id and not is_admin:
        return error_handler(403, 'You are not allowed to edit this comment')

    comment.update(content=request.json.get('content'))
    return jsonify(comment.to_dict()), 200

@comment_routes.route('/deleteComment/<comment_id>', methods=['DELETE'])
@token_required
def delete_comment(user_data, comment_id):
    comment = Comment.objects.get_or_404(id=comment_id)
    user_id = user_data.get('id')
    is_admin = user_data.get('isAdmin')

    if comment.user_id != user_id and not is_admin:
        return error_handler(403, 'You are not allowed to delete this comment')

    comment.delete()
    return jsonify({'message': 'Comment has been deleted'}), 200

@comment_routes.route('/getcomments', methods=['GET'])
@token_required
def get_comments(user_data):
    if not user_data.get('isAdmin'):
        return error_handler(403, 'You are not allowed to get all comments')

    start_index = int(request.args.get('startIndex', 0))
    limit = int(request.args.get('limit', 9))
    sort_direction = -1 if request.args.get('sort') == 'desc' else 1

    comments = Comment.objects.order_by('created_at', sort_direction).skip(start_index).limit(limit)
    total_comments = Comment.objects.count()
    last_month_comments = Comment.objects.filter(created_at__gte=datetime.now() - timedelta(days=30)).count()

    return jsonify({
        'comments': [comment.to_dict() for comment in comments],
        'totalComments': total_comments,
        'lastMonthComments': last_month_comments
    }), 200
