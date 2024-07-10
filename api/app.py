import os
from flask import Flask, send_from_directory, request, make_response
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Post, Comment

load_dotenv()

app = Flask(__name__, static_folder="../client/dist", static_url_path="/")
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key')

migrate = Migrate(app, db, render_as_batch=True)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

CORS(app)

from routes.user_route import user_routes
from routes.auth_route import auth_routes
from routes.post_route import post_routes
from routes.comment_route import comment_routes

app.register_blueprint(user_routes, url_prefix="/api/user")
app.register_blueprint(auth_routes, url_prefix="/api/auth")
app.register_blueprint(post_routes, url_prefix="/api/post")
app.register_blueprint(comment_routes, url_prefix="/api/comment")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


@app.errorhandler(Exception)
def handle_exception(e):
    status_code = getattr(e, "status_code", 500)
    message = getattr(e, "message", "Internal Server Error")
    return {
        "success": False,
        "statusCode": status_code,
        "message": message,
    }, status_code


if __name__ == "__main__":
    app.run(port=3000, debug=True)
