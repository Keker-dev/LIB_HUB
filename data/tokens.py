from flask import jsonify, g
from .session_db import db_sess
from .users_api import blueprint as bp
from .auth import basic_auth, token_auth

@bp.route('/api/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    global db_sess
    g.current_user.revoke_token()
    db_sess.commit()
    return '', 204


@bp.route('/api/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    global db_sess
    token = g.current_user.get_token()
    db_sess.commit()
    return jsonify({'token': token})
