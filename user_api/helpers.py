# -*- coding: utf-8 -*-
"""
Contains helpers to help construct objects.
"""

from .user_api import UserApi
from .db_manager import DBManager
from .authentication import Authentication


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
        db_manager=DBManager(db_url),
        authentication=Authentication(
            jwt_lifetime=jwt_lifetime,
            jwt_secret=u"DUMMY"
        )
    )


