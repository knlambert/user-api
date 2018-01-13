# coding: utf-8

from flask import Flask
from user_api import create_user_api

# create flask server
app = Flask(__name__)
app.debug = True

# Create user api object
user_api = create_user_api(
    db_url=u"mysql://root:localroot1234@127.0.0.1/user_api",
    jwt_secret=u"DUMMY"
)

# Register the blueprint
app.register_blueprint(
    user_api.get_flask_adapter().construct_users_blueprint(),
    url_prefix=u"/api/users"
)

# Run flask server
app.run(port=5000, debug=True)

