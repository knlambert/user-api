# coding: utf-8

from flask import Flask
from user_api.user_api import UserApi

# create flask server
app = Flask(__name__)
app.debug = True

# Create user api object
user_api = UserApi(
    db_host=u"127.0.0.1",
    db_user=u"root",
    db_passwd=u"localroot1234",
    db_name=u"user_api",
    jwt_secret=u"DUMMY",
    jwt_lifetime=30 * 24 * 3600
)

# Register the blueprint
app.register_blueprint(
    user_api.get_flask_adapter().construct_blueprint(),
    url_prefix=u"/api/users"
)

# Run flask server
app.run(port=5000, debug=True)

