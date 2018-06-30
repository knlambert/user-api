# coding: utf-8

import re
import base64
from functools import wraps
from flask import request, redirect
from user_api.user_api_exception import (
    ApiUnauthorized
)
from .flask_utils import add_api_error_handler
from .user_api_blueprint import construct_user_api_blueprint
from .role_api_blueprint import construct_role_api_blueprint


class FlaskUserApi(object):

    def __init__(self, user_api):
        """
        Construct the object.
        Args:
            user_api (UserApi): Injected User API
        """
        self._user_api = user_api

    def check_token(self, request, login_url=None):
        if u"Authorization" in request.headers:
            authorization = request.headers.get(u"Authorization")
            m = re.search(u"Bearer (\S+)", authorization)
            token = m.group(1)
            if m is None or not self._user_api.is_token_valid(token):
                raise ApiUnauthorized(u"Invalid token.")
            return token
        elif u"user-api-credentials" in request.cookies:
            decoded_token = base64.b64decode(request.cookies.get(u'user-api-credentials'))
            if not self._user_api.is_token_valid(decoded_token):
                raise ApiUnauthorized(u"Invalid token.")
            return decoded_token
        else:
            if login_url:
                return redirect(login_url, 302)
            else:
                raise ApiUnauthorized()

    def is_connected(self, login_url=None):

        def decorator(funct):

            @wraps(funct)
            def wrapper(*args, **kwargs):
                self.check_token(request, login_url)
                # If all right, do call function
                ret = funct(*args, **kwargs)
                return ret

            return wrapper

        return decorator

    def has_roles(self, roles):

        def decorator(funct):

            @wraps(funct)
            def wrapper(*args, **kwargs):

                self._user_api.token_has_roles(
                    token=self.check_token(request),
                    roles=roles
                )

                ret = funct(*args, **kwargs)
                return ret

            return wrapper

        return decorator
    
    @staticmethod
    def add_api_error_handler(blueprint):
        """
        Handle API errors.
        Args:
            blueprint (Blueprint): The blueprint to handle errors form.

        """
        add_api_error_handler(blueprint)
        
    def construct_user_api_blueprint(self):
        return construct_user_api_blueprint(self)

    def construct_role_api_blueprint(self):
        return construct_role_api_blueprint(self)
