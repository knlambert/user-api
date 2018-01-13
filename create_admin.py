# coding: utf-8

from user_api.db.db_manager import DBManager
from user_api.auth.auth_manager import AuthManager
import MySQLdb

# Init DB Manager
db_manager = DBManager(
    MySQLdb,
    db_host=u"127.0.0.1",
    db_user="root",
    db_passwd="localroot1234",
    db_name="user_api"
)
# Init Auth Manager
auth = AuthManager(
    jwt_secret=u"DUMMY",
    jwt_lifetime=30 * 24 * 3600
)

salt = auth.generate_salt()
hash = auth.generate_hash(u"DummyPassword", salt)
db_manager.save_new_user(
    email=u"admin@myapp.net",
    name=u"Admin",
    hash=hash,
    salt=salt
)