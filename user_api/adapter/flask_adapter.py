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
    ApiNotFound,
    ApiException,
    ApiForbidden,
    ApiUnauthorized,
    ApiUnprocessableEntity
)
import base64
import re


class FlaskAdapter(object):

    def __init__(self, user_api):
        """
        Construct the object.
        Args:
            user_api (UserApi): Injected User API
        """
        self._user_api = user_api

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
                        if m is None or not self._user_api.is_token_valid(token):
                            raise ApiUnauthorized(u"Invalid token.")

                    elif u"user-api-credentials" in request.cookies:
                        decoded_token = base64.b64decode(request.cookies.get(u'user-api-credentials'))
                        if not self._user_api.is_token_valid(decoded_token):
                            raise ApiUnauthorized(u"Invalid token.")
                    else:
                        if login_url:
                            return redirect(login_url, 302)
                        else:
                            raise ApiUnauthorized()

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

            token_payload, token = self._user_api.authenticate(**payload)

            response = jsonify(token_payload)
            response.set_cookie(
                u"user-api-credentials",
                value=base64.b64encode(token.encode(u"utf8")),
                httponly=True,
                expires=token_payload[u"exp"]
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
            result = self._user_api.reset_password(**payload)
            return flask_construct_response(result, 200)

        @user_api_blueprint.route(u'/', methods=[u"POST"])
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
            return flask_construct_response(self._user_api.register(**payload), 201)

        @user_api_blueprint.route(u'/me', methods=[u"GET"])
        @self.is_connected()
        def me():
            if u"user-api-credentials" in request.cookies:
                decoded_token = base64.b64decode(request.cookies.get(u'user-api-credentials'))
                return flask_construct_response(self._user_api.get_token_data(decoded_token), 200)

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
            return jsonify(self._user_api.list_users(**args)), 200

        @user_api_blueprint.route(u'/<int:user_id>', methods=[u"PUT"])
        @self.is_connected()
        @flask_check_and_inject_payload({
            u"email": {
                u"type": u"string",
                u"required": True
            },
            u"id": {
                u"type": u"integer",
                u"required": False
            },
            u"name": {
                u"type": u"string",
                u"required": True
            },
            u"active": {
                u"type": u"boolean",
                u"required": True
            }
        })
        def update(payload, user_id):
            if u"id" in payload:
                del payload[u"id"]

            result = self._user_api.update(payload, user_id)
            return flask_construct_response(result, 200)

        @user_api_blueprint.errorhandler(ApiException)
        def api_error_handler(exception):
            return flask_constructor_error(
                exception.message,
                exception.status_code,
                custom_error_code=exception.api_error_code,
                error_payload=exception.payload
            )

        return user_api_blueprint




