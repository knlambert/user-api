# coding: utf-8

from user_api.db_manager import DBManager
from user_api.authentication import Authentication
from user_api.decorator import is_connected
from config import CONFIG
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
auth = Authentication(
    jwt_secret=CONFIG[u"auth"][u"token"][u"secret"],
    jwt_lifetime=CONFIG[u"auth"][u"token"][u"lifetime"]
)

salt = auth.generate_salt()
hash = auth.generate_hash(u"DummyPassword", salt)
db_manager.save_new_user(
    email=u"admin@myapp.net",
    name=u"Admin",
    hash=hash,
    salt=salt
)