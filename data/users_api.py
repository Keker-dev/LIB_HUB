import flask
from flask import Blueprint, jsonify, make_response, request, session, abort
from . import db_session
from .users import User
from .tags import Tag
from .users import User

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
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    if all(usr_data):
        return make_response(jsonify({'error': 'You are already registered.'}), 403)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['name', 'about', 'email', "password"]):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    usr = User(name=request.json["name"], about=request.json["about"], email=request.json["email"])
    usr.set_password(request.json["password"])
    db_sess.add(usr)
    db_sess.commit()
    session["id"] = usr.id
    session["email"] = usr.email
    session["name"] = usr.name
    return jsonify({"success": True, 'id': usr.id, "name": usr.name})


@blueprint.route('/api/users/<user_name>/books', methods=['GET'])
def get_books(user_name):
    user = db_sess.query(User).filter(User.name == user_name).first()
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify({"books": [item.to_dict() for item in user.books]})


@blueprint.route('/api/users', methods=['DELETE'])
def delete_user():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                     User.name == usr_data[2]).first()
    if not usr or not all(usr_data):
        return make_response(jsonify({'error': 'You are not registered.'}), 403)
    session.pop("id")
    session.pop("email")
    session.pop("name")
    db_sess.delete(usr)
    db_sess.commit()
    return jsonify({"success": True})


@blueprint.route('/api/users/logout')
def logout_user():
    usr_data = [session.get("id", None), session.get("email", None), session.get("name", None)]
    usr = db_sess.query(User).filter(User.id == usr_data[0], User.email == usr_data[1],
                                     User.name == usr_data[2]).first()
    if not usr or not all(usr_data):
        return make_response(jsonify({'error': 'You are not registered.'}), 403)
    session.pop("id")
    session.pop("email")
    session.pop("name")
    return jsonify({"success": True})
