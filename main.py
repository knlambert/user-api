# coding: utf-8
# coding: utf-8

from flask import Flask
from user_api.user_api import UserApi 
from user_api.flask_user_api import FlaskUserApi 
from config import CONFIG

# create flask server
app = Flask(__name__)

# Create user api object
user_api = UserApi(
    db_host=u"127.0.0.1",
    db_user=u"root",
    db_passwd=u"localroot1234",
    db_name=u"user_api",
    jwt_secret=CONFIG[u"auth"][u"token"][u"secret"],
    jwt_lifetime=CONFIG[u"auth"][u"token"][u"lifetime"]
)

# Use flask shortcut
flask_user_api = FlaskUserApi(user_api)

# Register the blueprint
app.register_blueprint(
    flask_user_api.construct_blueprint(), 
    url_prefix=u"/api/user"
)

# Run flask server
app.run(port=5000, debug=True)

