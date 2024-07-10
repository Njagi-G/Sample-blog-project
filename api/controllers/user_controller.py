import bcrypt
from flask import jsonify, request
from models import User
from utils.error import error_handler
from app import app, db

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'API is working!'})

@app.route('/api/update/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user or str(user.id) != user_id:
        return error_handler(403, 'You are not allowed to update this user')

    if 'password' in request.json and request.json['password']:
        if len(request.json['password']) < 6:
            return error_handler(400, 'Password must be at least 6 characters')
        hashed_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password.decode('utf-8')

    if 'username' in request.json and request.json['username']:
        username = request.json['username']
        if len(username) < 7 or len(username) > 20:
            return error_handler(400, 'Username must be between 7 and 20 characters')
        if ' ' in username:
            return error_handler(400, 'Username cannot contain spaces')
        if username != username.lower():
            return error_handler(400, 'Username must be lowercase')
        if not username.isalnum():
            return error_handler(400, 'Username can only contain letters and numbers')
        user.username = username

    if 'email' in request.json and request.json['email']:
        user.email = request.json['email']

    if 'profilePicture' in request.json and request.json['profilePicture']:
        user.profile_picture = request.json['profilePicture']

    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/api/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user or (not user.is_admin and str(user.id) != user_id):
        return error_handler(403, 'You are not allowed to delete this user')

    db.session.delete(user)
    db.session.commit()
    return jsonify('User has been deleted')

@app.route('/api/signout', methods=['POST'])
def signout():
    return jsonify('User has been signed out')

@app.route('/api/getusers', methods=['GET'])
def get_users():
    if not request.args.get('isAdmin'):
        return error_handler(403, 'You are not allowed to see all users')

    start_index = int(request.args.get('startIndex', 0))
    limit = int(request.args.get('limit', 9))
    sort_direction = 1 if request.args.get('sort') == 'asc' else -1

    users = User.query.order_by(User.created_at.desc()).slice(start_index, start_index + limit).all()
    total_users = User.query.count()

    from datetime import datetime, timedelta
    one_month_ago = datetime.now() - timedelta(days=30)
    last_month_users = User.query.filter(User.created_at >= one_month_ago).count()

    return jsonify({
        'users': [user.to_dict() for user in users],
        'totalUsers': total_users,
        'lastMonthUsers': last_month_users
    })

@app.route('/api/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_handler(404, 'User not found')
    return jsonify(user.to_dict())
