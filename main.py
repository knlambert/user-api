# coding: utf-8

from flask import Flask, jsonify
from user_api import create_user_api

# create flask server
app = Flask(__name__)
app.debug = True


def on_user_created(user):
    print(u"CREATED {}".format(user))


def on_user_updated(user):
    print(u"UPDATED {}".format(user))


# Create user api object
user_api = create_user_api(
    db_url=u"mysql+mysqlconnector://user_api_sa:password@127.0.0.1/user_api",
    jwt_secret=u"dummy_secret",
    user_created_callback=on_user_created,
    user_updated_callback=on_user_updated
)

flask_user_api = user_api.get_flask_user_api()

# Register the blueprint
app.register_blueprint(flask_user_api.construct_user_api_blueprint(), url_prefix=u"/api/users")
app.register_blueprint(flask_user_api.construct_role_api_blueprint(), url_prefix=u"/api/roles")


@app.route(u"/hello")
@flask_user_api.has_roles([u"admin"])
def hello_world():
    return jsonify({
        u"message": u"hello"
    }), 200


# Run flask server
app.run(port=5001, debug=True)

