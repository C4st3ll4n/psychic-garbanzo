from flask import Blueprint, jsonify, request, make_response
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user

user_blueprint = Blueprint("user_api_routes",
                           __name__,
                           url_prefix="/api/v1/user")


@user_blueprint.route('/')
def index():
    return "HI !"


@user_blueprint.route('/all', methods=["GET"])
def get_all_users():
    users = User.query.all()
    serialized_users = [u.serialize() for u in users]
    response = {
        "message": "Returning all users",
        "users": serialized_users
    }

    return make_response(jsonify(response), 200)


@user_blueprint.route('/', methods=["POST"])
def create_user():
    try:
        user = User()
        user.username = request.form['username']
        user.password = generate_password_hash(request.form['password'], method='sha256')
        user.is_admin = True

        db.session.add(user)
        db.session.commit()

        response = {
            "message": "User created",
            "user": user.serialize()
        }

        status_code = 201

    except Exception as e:
        print(str(e))
        response = {
            "message": "Error in creating user",
        }

        status_code = 400

    return make_response(jsonify(response), status_code)


@user_blueprint.route('/login', methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if not user:
        return make_response(jsonify({
            "message": "User not found"
        }), 401)

    if check_password_hash(user.password, password):
        user.update_api_key()
        db.session.commit()
        login_user(user)

        return make_response(jsonify({
            "message": "User logged in",
            "api_key": user.api_key
        }), 200)

    return make_response(jsonify({
        "message": "Access denied"
    }))


@user_blueprint.route('/logout', methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()

        return make_response(jsonify({
            "message": "Logged out"
        }), 200)

    return make_response(jsonify({
        "message": "No user authenticated"
    }), 401)


@user_blueprint.route('/<username>/exists', methods=["GET"])
def user_exists(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return make_response(jsonify({
            "message": "Exists",
            "result": True
        }), 200)

    return make_response(jsonify({
        "message": "Do not exists",
    }), 404)


@user_blueprint.route('/me', methods=["GET"])
def account_data():
    if current_user.is_authenticated:
        return make_response(jsonify({
            "user": current_user.serialize()
        }), 200)

    return make_response(jsonify({
        "message": "No user authenticated"
    }), 401)
