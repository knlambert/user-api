
# Introduction

This repository is a python lib designed to handle the authentication on my personal projects. 
The projects uses :
 - Python2.
 - MySQL.
 - Flask.
 - PBKDF2 algorithm.
 - A JWT token.

# Setting up

## Installation

To install the lib :

```bash
pip2 install https://github.com/duckswitch/py-duck-user-api.git
```

## The database

Execute the database/schema.sql file given in the repository.

```sql
source database/schema.sql
```

## Integration

### Hello auth
You can have a config.py file at the root of your flask App, with a CONFIG variable in it.
Here the adviced structure (you can add anything you want in this config, but do not use the auth section).

```python
CONFIG = {
    u"auth": {
        u"token": {
            u"lifetime": 24 * 3600 * 30, # 30 days.
            u"secret": u"DUMMYSECRET" # Do put a real secret there.
        }
    }
}
```

Then, declare the necessary webservices :

```python
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
```

### Authentify my custom web services (Flask)

Just use the built-in "is_connected" decorator for flask.

```python
app = Flask(__name__)

@app.route(u'/dummy', methods=[u'GET'])
@user_api.is_connected 
def dummy_route():
    return jsonify({
        "message": "Let's rock !"
    })
```


# Web services

## How to authentify ?

Some services will send you a 401 if your are not authenticated.
To evoid that, do not forget to set the authentication header.
The API also works with a cookie (name it "credentials" with the token as value).

```bash
Authentication: Bearer eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0
```

## Services 
The web services are declared in the user_api/blueprint.py file.
HTTPS is strongly recommended.

### Authentify

Use this service to authentify your user.
Send user & password, then get a token.

```bash
POST api/user/authentify
{
  "email": "dummy@dummy.net",
  "password": "JustMyPassword"
}

200
{
  "token": "eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0"
}
```

### Reset password [Authenticated]

Use this service to reset the password of a user.
Send email & password, get an updated Token.

```bash
POST api/user/reset_password
{
    "email": "dummy@dummy.net",
    "password": "JustMyPassword"
}

200
{
  "token": "eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0"
}
```

### Register a new user [Authenticated]

Use this web service to create a user.
```bash
POST api/user/register
{
    "email": "dummy@dummy.net",
    "password": "JustMyPassword",
    "name": "Dummy Doe"
}

201
{
  "token": "eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0"
}
```

### Check token [Authenticated]

When your user is authenticated, the password should never be sent again.
Then, use this service to check the token, and extract the informations stored inside.
Please pay attention to the "exp" field. This is an UTC timestamp giving you the expiration date of the token.

Past this time, the token is not going to work anymore.

```bash
POST /token/check/
{
    "token": "eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0"
}

200
{
  "email": "dummy@dummy.net", 
  "exp": 1497989335, 
  "id": 2, 
  "name": "Dummy Doe"
}
```
