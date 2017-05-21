# coding: utf-8

import MySQLdb
from .authentication import Authentication
from .db_manager import DBManager 


class UserApi(object):


    def __init__(
        self,
        db_host=u"127.0.0.1",
        db_user=None,
        db_passwd=None,
        db_name=u"user_api",
        jwt_secret=None,
        jwt_lifetime=3600 * 24 * 60,
        db_manager=None,
        authentication=None
    ):
    
        self.db_manager = db_manager or DBManager(
            MySQLdb,
            db_host=db_host,
            db_user=db_user,
            db_passwd=db_passwd,
            db_name=db_name
        )

        self.authentication = authentication or Authentication(
            jwt_secret=jwt_secret,
            jwt_lifetime=jwt_lifetime
        )