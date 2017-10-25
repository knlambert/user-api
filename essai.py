# -*- coding: utf-8 -*-
"""
Contains the DB manager.
"""
from user_api.db_manager import DBManager
import json
import MySQLdb
import logging

db_manager = DBManager(
    MySQLdb,
    db_host=u"127.0.0.1",
    db_unix_socket=None,
    db_user=u"root",
    db_passwd=u"localroot1234",
    db_name=u"user_api"
)

result = db_manager.list_users(email=u"kevin")
print(json.dumps(result, indent=4))