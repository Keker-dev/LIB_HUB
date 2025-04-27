import flask
from flask import Blueprint, jsonify, make_response, request, session, abort
from . import db_session
from .tags import Tag
from .users import User
from .auth import token_auth

blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)
db_sess = None


@blueprint.route('/api/users/<user_name>', methods=['GET'])
def get_one_user(user_name):
    usr = db_sess.query(User).filter(User.name == user_name).first()
    if not usr:
        return make_response(jsonify({'error': 'The user was not found'}), 404)
    return jsonify({'user': {"name": usr.name, "about": usr.about, "likes": usr.likes_count, "reg_date": usr.reg_date}})


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['name', 'about', 'email', "password"]):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    usr = User(name=request.json["name"], about=request.json["about"], email=request.json["email"])
    usr.set_password(request.json["password"])
    usr.get_token()
    db_sess.add(usr)
    db_sess.commit()
    return jsonify({"success": True, 'id': usr.id, "name": usr.name, "token": usr.get_token(),
                    "token_expiration": usr.token_expiration})


@blueprint.route('/api/users/<user_name>/books', methods=['GET'])
def get_books(user_name):
    user = db_sess.query(User).filter(User.name == user_name).first()
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify({"books": [item.to_dict() for item in user.books]})


@blueprint.route('/api/users/comments', methods=['GET'])
@token_auth.login_required
def get_comments():
    token = request.headers["Authorization"]
    if "Bearer" in token:
        token = token[7:]
    usr = User.check_token(token)
    if not usr:
        return make_response(jsonify({'error': 'User not found or token expired.'}), 403)
    return jsonify({"comments": [item.to_dict() for item in usr.comments]})


@blueprint.route('/api/users', methods=['DELETE'])
@token_auth.login_required
def delete_user():
    token = request.headers["Authorization"]
    if "Bearer" in token:
        token = token[7:]
    usr = User.check_token(token)
    if not usr:
        return make_response(jsonify({'error': 'User not found or token expired.'}), 403)
    db_sess.delete(usr)
    db_sess.commit()
    return jsonify({"success": True})


@blueprint.route('/api/users', methods=['PUT'])
@token_auth.login_required
def update_user():
    token = request.headers["Authorization"]
    if "Bearer" in token:
        token = token[7:]
    usr = User.check_token(token)
    if not usr:
        return make_response(jsonify({'error': 'User not found or token expired.'}), 403)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    if request.json.get("name"):
        if db_sess.query(User).filter(User.name == request.json.get("name")).first():
            return make_response(jsonify({'error': 'That name is already taken.'}), 403)
        usr.name = request.json.get("name")
    if request.json.get("email"):
        if db_sess.query(User).filter(User.email == request.json.get("email")).first():
            return make_response(jsonify({'error': 'That email is already taken.'}), 403)
        usr.email = request.json.get("email")
    if request.json.get("about"):
        usr.about = request.json.get("about")
    if request.json.get("password"):
        usr.set_password(request.json.get("password"))
    if request.json.get("settings"):
        usr.settings = request.json.get("settings")
    db_sess.commit()
    return jsonify({"success": True, 'id': usr.id, "name": usr.name, "token": usr.get_token(),
                    "token_expiration": usr.token_expiration})
