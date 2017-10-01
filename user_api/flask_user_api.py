# coding: utf-8

from functools import wraps
from flask import request, jsonify, Blueprint, redirect
import base64
import re
import json


class FlaskUserApi(object):

    def __init__(self, user_api):
        self.user_api = user_api

    def is_connected(self, login_url=None):

        def decorator(funct):
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
                                u"message": u"Invalid token."
                            }), 401
                    elif u"user-api-credentials" in request.cookies:
                        decoded_token = base64.b64decode(request.cookies.get(u'user-api-credentials'))
                        if not self.user_api.authentication.is_token_valid(decoded_token):
                            return jsonify({
                                u"message": u"Invalid token."
                            }), 401
                    else:
                        if login_url:
                            return redirect(login_url, 302)
                        else:
                            return jsonify({
                                u"message": u"Forbidden."
                            }), 403

                    # If all right, do call function
                ret = funct(*args, **kwargs)
                return ret

            return wrapper

        return decorator

    def construct_blueprint(self):
        user_api_blueprint = Blueprint(u'user_api', __name__)

        @user_api_blueprint.route(u'/login', methods=[u"POST"])
        def login():
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
                        payload = self.user_api.db_manager.get_user_information(email=email)
                        token = self.user_api.authentication.generate_token(payload)
                    else:
                        raise ValueError(u"Wrong password")

                    response = jsonify(payload)
                    response.set_cookie(
                        u"user-api-credentials",
                        value=base64.b64encode(token.encode(u"utf8")),
                        httponly=True,
                        expires=payload[u"exp"]
                    )

                    return response, 200

                except ValueError:
                    return jsonify({
                        u"message": u"Wrong login or / and password."
                    }), 401
            else:
                return jsonify({
                    u"message": u"Missing parameters."
                }), 422

        @user_api_blueprint.route(u'/reset-password', methods=[u'POST'])
        @self.is_connected()
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
                    payload = self.user_api.db_manager.get_user_information(email=email)
                    if payload is None:
                        raise ValueError(u"User '{}' doesn't exist.".format(email))

                    return jsonify(payload), 200
                except ValueError as e:
                    return jsonify({
                        u"message": e.message
                    }), 401
            else:
                return jsonify({
                    u"message": u"Missing parameters."
                }), 422

        @user_api_blueprint.route(u'/register', methods=[u"POST"])
        @self.is_connected()
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

        @user_api_blueprint.route(u'/me', methods=[u"GET"])
        @self.is_connected()
        def me():
            if u"user-api-credentials" in request.cookies:
                decoded_token = base64.b64decode(request.cookies.get(u'user-api-credentials'))
                return jsonify(self.user_api.authentication.get_token_data(decoded_token)), 200

        @user_api_blueprint.route(u'/logout', methods=[u"GET"])
        @self.is_connected()
        def logout():
            if u"user-api-credentials" in request.cookies:
                response = jsonify({
                    u"message": u"User disconnected."
                })
                response.set_cookie(
                    u"user-api-credentials",
                    value=u"",
                    httponly=True,
                    expires=0
                )
                return response, 200

        return user_api_blueprint




