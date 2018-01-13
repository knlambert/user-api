# -*- coding: utf-8 -*-
"""
Contains helpers to help construct objects.
"""

from .user_api import UserApi
from .db.db_user_manager import DBUserManager
from .db.db_role_manager import DBRoleManager
from .auth.auth_manager import AuthManager


def create_user_api(db_url, jwt_secret, jwt_lifetime=3600 * 12 * 30):
    """
    Create a user API method.
    Args:
        db_url (unicode): The DB url for connection.
        jwt_secret (unicode): The secret used to generate tokens.
        jwt_lifetime (unicode): How long each token is valid.

    Returns:
        (UserApi): The constructed UserApi object.
    """
    return UserApi(
        db_user_manager=DBUserManager(db_url),
        db_role_manager=DBRoleManager(db_url),
        auth_manager=AuthManager(
            jwt_lifetime=jwt_lifetime,
            jwt_secret=jwt_secret
        )
    )


