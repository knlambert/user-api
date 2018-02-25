# coding: utf-8

from functools import wraps
from flask import request, jsonify, Blueprint, redirect
from flask_utils import (
    flask_check_args,
    flask_constructor_error,
    flask_construct_response,
    flask_check_and_inject_payload
)
from user_api.user_api_exception import (
    ApiConflict,
    ApiException,
    ApiForbidden,
    ApiUnauthorized,
    ApiUnprocessableEntity
)
import base64
import re
import json


class FlaskAdapter(object):

    def __init__(self, db_manager, authentication):
        """
        Construct the object.
        Args:
            db_manager (DBManager): Injected DB manager.
            authentication (Authentication): Injected Authentication object.
        """
        self._db_manager = db_manager
        self._authentication = authentication

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
                        if m is None or not self._authentication.is_token_valid(token):
                            raise ApiUnauthorized(u"Invalid token.")

                    elif u"user-api-credentials" in request.cookies:
                        decoded_token = base64.b64decode(request.cookies.get(u'user-api-credentials'))
                        if not self._authentication.is_token_valid(decoded_token):
                            raise ApiUnauthorized(u"Invalid token.")
                    else:
                        if login_url:
                            return redirect(login_url, 302)
                        else:
                            raise ApiForbidden()

                    # If all right, do call function
                ret = funct(*args, **kwargs)
                return ret

            return wrapper

        return decorator

    def construct_blueprint(self):
        user_api_blueprint = Blueprint(u'user_api', __name__)

        @user_api_blueprint.route(u'/login', methods=[u"POST"])
        @flask_check_and_inject_payload({
            u"email": {
                u"type": u"string",
                u"required": True
            },
            u"password": {
                u"type": u"string",
                u"required": True
            }
        })
        def login(payload):
            email = payload.get(u"email")
            password = payload.get(u"password")
            salt = self._db_manager.get_user_salt(email=email)
            hash = self._authentication.generate_hash(
                password,
                salt
            )
            valid = self._db_manager.is_user_hash_valid(
                email,
                hash=hash
            )

            if valid:
                payload = self._db_manager.get_user_information(email=email)
                token = self._authentication.generate_token(payload)
            else:
                raise ApiUnauthorized(u"Wrong login or / and password.")

            response = jsonify(payload)
            response.set_cookie(
                u"user-api-credentials",
                value=base64.b64encode(token.encode(u"utf8")),
                httponly=True,
                expires=payload[u"exp"]
            )

            return response, 200

        @user_api_blueprint.route(u'/reset-password', methods=[u'POST'])
        @self.is_connected()
        @flask_check_and_inject_payload({
            u"email": {
                u"type": u"string",
                u"required": True
            },
            u"password": {
                u"type": u"string",
                u"required": True
            }
        })
        def reset_password(payload):
            salt = self._authentication.generate_salt()
            email = payload.get(u"email")
            password = payload.get(u"password")
            hash = self._authentication.generate_hash(password, salt)

            self._db_manager.modify_hash_salt(email, hash, salt)
            payload = self._db_manager.get_user_information(email=email)
            if payload is None:
                raise ApiUnprocessableEntity(u"User '{}' doesn't exist.".format(email))

            return flask_construct_response(payload, 200)

        @user_api_blueprint.route(u'/register', methods=[u"POST"])
        @self.is_connected()
        @flask_check_and_inject_payload({
            u"email": {
                u"type": u"string",
                u"required": True
            },
            u"name": {
                u"type": u"string",
                u"required": True
            },
            u"password": {
                u"type": u"string",
                u"required": True
            }
        })
        def register(payload):
            try:
                salt = self._authentication.generate_salt()
                hash = self._authentication.generate_hash(payload.get(u"password"), salt)
                self._db_manager.save_new_user(
                    email=payload.get(u"email"),
                    name=payload.get(u"name"),
                    hash=hash,
                    salt=salt
                )
            except ValueError:
                raise ApiConflict(u"User already exists.")

            return flask_construct_response({
                u"message": u"New user registered successfully."
            }, 201)

        @user_api_blueprint.route(u'/me', methods=[u"GET"])
        @self.is_connected()
        def me():
            if u"user-api-credentials" in request.cookies:
                decoded_token = base64.b64decode(request.cookies.get(u'user-api-credentials'))
                return flask_construct_response(self._authentication.get_token_data(decoded_token), 200)

        @user_api_blueprint.route(u'/logout', methods=[u"GET"])
        @self.is_connected()
        def logout():
            if u"user-api-credentials" in request.cookies:
                response, code = flask_construct_response({
                    u"message": u"User disconnected."
                }, 200)
                response.set_cookie(
                    u"user-api-credentials",
                    value=u"",
                    httponly=True,
                    expires=0
                )
                return response, code

        @user_api_blueprint.route(u'/', methods=[u"GET"])
        @self.is_connected()
        @flask_check_args({
            u"limit": {
                u"type": u"integer",
                u"default": 20,
                u"coerce": int
            },
            u"offset": {
                u"type": u"integer",
                u"default": 0,
                u"coerce": int
            },
            u"email": {
                u"type": u"string"
            },
            u"name": {
                u"type": u"string"
            }
        })
        def list_users(args):
            return jsonify(self._db_manager.list_users(**args)), 200

        @user_api_blueprint.errorhandler(ApiException)
        def api_error_handler(exception):
            return flask_constructor_error(
                exception.message,
                exception.status_code,
                custom_error_code=exception.api_error_code,
                error_payload=exception.payload
            )

        @user_api_blueprint.errorhandler(ApiException)
        def api_error_handler(exception):
            return self.api_error_handler(exception)

        return user_api_blueprint

    @staticmethod
    def api_error_handler(exception):
        """
        Return the error handler associated to the API.
        Returns:
            (callable): The error handler.
        """
        return flask_constructor_error(
            exception.message,
            exception.status_code,
            custom_error_code=exception.api_error_code,
            error_payload=exception.payload
        )




