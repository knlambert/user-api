# coding: utf-8

from .db_manager import DBManager
from .authentication import Authentication
from functools import wraps
from flask import request, jsonify, Blueprint
import re
import json


class FlaskUserApi(object):

    def __init__(self, user_api):
        self.user_api = user_api

    def is_connected(self, funct):
        @wraps(funct)
        def wrapper(*args, **kwargs):
            # These two endpoint do not hae self.user_api.authentication.
            if request.endpoint not in [u'user_api.authentify']:
                if u"Authorization" in request.headers:
                    authorization = request.headers.get(u"Authorization")
                    m = re.search(u"Bearer (\S+)", authorization)
                    token = m.group(1)
                    if m is None or not self.user_api.authentication.is_token_valid(token):
                        return jsonify({
                            u"Message": u"Invalid token."
                        }), 401
                elif u"credentials" in request.cookies:
                    decoded = base64.b64decode(request.cookies.get('credentials'))
                    credentials = json.loads(decoded)
                    if not self.user_api.authentication.is_token_valid(credentials.get('token')):
                        return jsonify({
                            u"Message": u"Invalid token."
                        }), 401
                else:
                    return jsonify({
                        u"Message": u"Unauthorized."
                    }), 403
                # If all right, do call function
            ret = funct(*args, **kwargs)
            return ret

        return wrapper

    def construct_blueprint(self):
        user_api_blueprint = Blueprint(u'user_api', __name__)

        @user_api_blueprint.route(u'/authentify', methods=[u"POST"])
        def authentify():
            try:
                data = json.loads(request.data, encoding=u"utf-8")
            except ValueError:
                return jsonify({
                    u"message": u"Invalid JSON."
                }), 422
            if u"password" in data and u"email" in data:
                try:
                    email = data.get(u"email")
                    password = data.get(u"password")
                    salt = self.user_api.db_manager.get_user_salt(email=email)
                    hash = self.user_api.authentication.generate_hash(
                        password,
                        salt
                    )
                    valid = self.user_api.db_manager.is_user_hash_valid(
                        email,
                        hash=hash
                    )

                    if valid:
                        payload = self.user_api.db_manager.get_user_informations(email=email)
                        token = self.user_api.authentication.generate_token(payload)
                    else:
                        raise ValueError(u"Wrong password")

                    return jsonify({
                        u"token": token
                    }), 200
                except ValueError:
                    return jsonify({
                        u"message": u"Wrong login or / and password."
                    }), 401
            else:
                return jsonify({
                    u"message": u"Missing parameters."
                }), 422

        @user_api_blueprint.route(u'/reset_password', methods=[u'POST'])
        @self.is_connected
        def reset_password():
            try:
                data = json.loads(request.data, encoding=u"utf-8")
            except ValueError:
                return jsonify({
                    u"message": u"Invalid JSON."
                }), 422
            if u"password" in data and u"email" in data:
                try:
                    salt = self.user_api.authentication.generate_salt()
                    email = data.get(u"email")
                    password = data.get(u"password")
                    hash = self.user_api.authentication.generate_hash(password, salt)

                    self.user_api.db_manager.modify_hash_salt(email, hash, salt)
                    payload = self.user_api.db_manager.get_user_informations(email=email)
                    token = self.user_api.authentication.generate_token(payload)

                    return jsonify({
                        u"token": token
                    }), 200
                except ValueError:
                    return jsonify({
                        u"message": u"Wrong login or / and password."
                    }), 401
            else:
                return jsonify({
                    u"message": u"Missing parameters."
                }), 422

        @user_api_blueprint.route(u'/register', methods=[u"POST"])
        @self.is_connected
        def register():
            try:
                data = json.loads(request.data, encoding=u"utf-8")
            except ValueError:
                return jsonify({
                    u"message": u"Invalid JSON."
                }), 422
            if u"password" in data and u"email" in data and u"name" in data:
                try:
                    salt = self.user_api.authentication.generate_salt()
                    hash = self.user_api.authentication.generate_hash(data.get(u"password"), salt)
                    self.user_api.db_manager.save_new_user(
                        email=data.get(u"email"),
                        name=data.get(u"name"),
                        hash=hash,
                        salt=salt
                    )
                except ValueError:
                    return jsonify({
                        u"message": u"User already exists."
                    }), 409
                return jsonify({
                    u"message": u"New user registered successfully."
                }), 201
            else:
                return jsonify({
                    u"message": u"Missing parameters."
                }),

        @user_api_blueprint.route(u'/token/check/', methods=[u"POST"])
        def check():
            try:
                data = json.loads(request.data, encoding=u"utf-8")
            except ValueError:
                return jsonify({
                    u"message": u"Invalid JSON."
                }), 422
            if u"token" in data:
                decoded = self.user_api.authentication.get_token_data(data[u"token"])
                if decoded is not None:
                    return jsonify(decoded), 200
                else:
                    return jsonify({
                        u"message": u"Invalid token."
                    }), 401
            else:
                return jsonify({
                    u"message": u"Missing parameters."
                }), 422

        return user_api_blueprint




