from flask import g, make_response, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from .users import User
from .tokens import Token

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@token_auth.verify_token
def verify_token(token):
    g.current_user = Token.get_user(token) if token else None
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error():
    return make_response(jsonify({'error': 'Unauthorized.'}), 401)


@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)


@basic_auth.error_handler
def basic_auth_error():
    return make_response(jsonify({'error': 'Unauthorized.'}), 401)
