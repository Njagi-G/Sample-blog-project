from flask import Blueprint, request
from controllers.user_controller import (
    delete_user,
    get_user,
    get_users,
    signout,
    test,
    update_user,
)

from api.utils.verifyUser import verify_token

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/test", methods=["GET"])
def test_route():
    return test()


@user_routes.route("/update/<user_id>", methods=["PUT"])
@verify_token
def update_user_route(user_id):
    return update_user(request, user_id)


@user_routes.route("/delete/<user_id>", methods=["DELETE"])
@verify_token
def delete_user_route(user_id):
    return delete_user(request, user_id)


@user_routes.route("/signout", methods=["POST"])
def signout_route():
    return signout(request)


@user_routes.route("/getusers", methods=["GET"])
@verify_token
def get_users_route():
    return get_users(request)


@user_routes.route("/<user_id>", methods=["GET"])
@verify_token
def get_user_route(user_id):
    return get_user(user_id)
