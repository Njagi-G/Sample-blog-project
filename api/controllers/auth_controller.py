from flask import Blueprint, request, jsonify, make_response
from models import User
import bcrypt
import jwt
import os
from utils import error_handler

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return error_handler(400, 'All fields are required')

    # Check if user with the same email already exists
    if User.objects.filter(email=email).count() > 0:
        return error_handler(400, 'User with this email already exists')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(username=username, email=email, password=hashed_password)
    new_user.save()

    return jsonify({'message': 'Signup successful'}), 200

@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return error_handler(400, 'All fields are required')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return error_handler(404, 'User not found')

    if not bcrypt.checkpw(password.encode('utf-8'), user.password):
        return error_handler(400, 'Invalid password')

    token = jwt.encode({'id': str(user.id), 'isAdmin': user.isAdmin}, os.environ.get('JWT_SECRET'), algorithm='HS256')

    response = make_response(jsonify({'id': str(user.id), 'username': user.username, 'email': user.email, 'isAdmin': user.isAdmin}))
    response.set_cookie('access_token', token, httponly=True)

    return response

@auth_bp.route('/google', methods=['POST'])
def google():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    google_photo_url = data.get('googlePhotoUrl')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        generated_password = bcrypt.hashpw(os.urandom(16), bcrypt.gensalt())
        username = name.lower().replace(' ', '') + str(os.urandom(4))
        new_user = User(username=username, email=email, password=generated_password, profilePicture=google_photo_url)
        new_user.save()
        user = new_user

    token = jwt.encode({'id': str(user.id), 'isAdmin': user.isAdmin}, os.environ.get('JWT_SECRET'), algorithm='HS256')

    response = make_response(jsonify({'id': str(user.id), 'username': user.username, 'email': user.email, 'isAdmin': user.isAdmin, 'profilePicture': user.profilePicture}))
    response.set_cookie('access_token', token, httponly=True)

    return response
