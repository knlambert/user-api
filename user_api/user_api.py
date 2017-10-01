# coding: utf-8

import MySQLdb
from .authentication import Authentication
from .db_manager import DBManager 


class UserApi(object):

    def __init__(
        self,
        db_host=None,
        db_user=None,
        db_passwd=None,
        db_name=u"user_api",
        db_unix_socket=None,
        jwt_secret=None,
        jwt_lifetime=3600 * 24 * 60,
        db_manager=None,
        authentication=None
    ):
    
        self.db_manager = db_manager or DBManager(
            MySQLdb,
            db_host=db_host,
            db_unix_socket=db_unix_socket,
            db_user=db_user,
            db_passwd=db_passwd,
            db_name=db_name
        )

        self.authentication = authentication or Authentication(
            jwt_secret=jwt_secret,
            jwt_lifetime=jwt_lifetime
        )
