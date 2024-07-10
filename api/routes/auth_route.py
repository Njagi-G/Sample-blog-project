from flask import Blueprint, request
from controllers.auth_controller import google, signin, signup

auth_routes = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_routes.route('/signup', methods=['POST'])
def signup_route():
    return signup()

@auth_routes.route('/signin', methods=['POST'])
def signin_route():
    return signin()

@auth_routes.route('/google', methods=['POST'])
def google_route():
    return google()
