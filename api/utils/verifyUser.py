import jwt
from flask import request, jsonify
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()

def verify_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            token = token.split(' ')[1]
            user = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        request.user = user
        return func(*args, **kwargs)

    return wrapper
