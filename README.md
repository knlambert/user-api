
# Introduction.

User API built with Python 3 and MySQL.

# Setting up.

## Installation.

To install the lib as a third party.

```bash
pip3 install user-api
```

## The database.

To generate the database and create the admin user, use the init_api.py script.
First set the dev env.
```sql
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
```
Then run the init script :
```bash
python3 init_api.py <db_url> \
    <jwt_secret> <admin_password> <user_api_sa_password>
```
with the following parameters :
- **db_url** : the connection to the database (mysql+mysqlconnector://root:<root_password>@<db_ip>)
- **jwt_secret** : A secret used to generate the JWT token.
- **admin_password**: The password given to the admin user which will be created.
- **user_api_sa_password** : The password for the created service account (to use in the API config).

## Run the API.

Use the main.py entry point :
```bash
source venv/bin/activate
python3 main.py
```

## Flask Integration.

### Base.
```python
from flask import Flask, jsonify
from user_api import create_user_api
# create flask server
app = Flask(__name__)
app.debug = True
# Custom callbacks.
def on_user_created(user):
    print("CREATED {}".format(user))

def on_user_updated(user):
    print("UPDATED {}".format(user))

# Create user api object
user_api = create_user_api(
    db_url="mysql+mysqlconnector://user_api_sa:password@127.0.0.1/user_api",
    jwt_secret="dummy_secret",
    user_created_callback=on_user_created,
    user_updated_callback=on_user_updated
)

flask_user_api = user_api.get_flask_user_api()

# Register the blueprints
app.register_blueprint(flask_user_api.construct_user_api_blueprint(), url_prefix="/api/users")
app.register_blueprint(flask_user_api.construct_role_api_blueprint(), url_prefix="/api/roles")

# Run flask server
app.run(port=5001, debug=True)
```

### Enable auth on an endpoint.

Use the built-in "is_connected" decorator for flask.

```python
@app.route(u'/dummy', methods=[u'GET'])
@user_api.is_connected 
def dummy_route():
    return jsonify({
        "message": "Let's rock !"
    })
```

### Enable role on an endpoint.

Use use the built-in "has_roles" decorator for flask.
```python
@app.route("/hello")
@flask_user_api.has_roles(["admin"])
def hello_world():
    return jsonify({
        "message": "hello"
    }), 200
```

# API

## How does the session work ?

Some services will send you a 401 if your are not authenticated.
To evoid that, do not forget to set the authentication header.
```bash
Authentication: Bearer eyJ0eXAiOisqdJKV1QiLCJhbGci1NiJ9.eyJlbWFpbCI6ImtldmluLmxhbWJlcnRAZGV2b3RlYW1nY2xvdWQuY29tIiwiZXhwIjoxNDkCJuYW1lIjoiS2V2aW4gTEFNQkVSVCIsImlkIjoyfQ.sBatRMvPKStk5vt9f2oCvxfM0ljqqsdqdqsrZPkEgVKsY0
```
The API also works with a auth cookie which is set server side at connection.

## Authentify

Use this service to connect your user.
Send email & password to get a token.

```bash
POST http://localhost:5001/api/users/login
```
Payload:
```json
{
	"email": "admin",
	"password": "password"
}
```
Result:
```json
{
    "active": true,
    "customer": {
        "id": 1
    },
    "email": "admin",
    "exp": 1535940278,
    "id": 1,
    "name": "admin",
    "roles": [
        {
            "code": "admin",
            "id": 1,
            "name": "Admin"
        }
    ]
}
```

## Reset password [Authenticated]

Use this service to reset the password of a user.
Send email & password, get an updated Token.

You must be connected to use this service.

```bash
POST http://localhost:5001/api/users/reset-password
```
Payload:
```json
{
	"email": "admin",
	"password": "password"
}
```
Result:
```json
{
    "active": true,
    "customer": {
        "id": 1
    },
    "email": "admin",
    "id": 1,
    "name": "admin"
}
```

## Register a new user [Authenticated]

Use this web service to create a user.

You must be connected to use this service.

```bash
POST http://localhost:5001/api/users/
```
Payload:
```json
{
	"email": "admin12",
	"name": "Admin2",
	"password": "password",
	"active": true,
	"roles": [{
		"id": 1
	}]
}
```
Result: 
```json
{
    "active": true,
    "customer": {
        "id": 1
    },
    "email": "admin12",
    "id": 2,
    "name": "Admin2",
    "roles": [
        {
            "code": "admin",
            "id": 1,
            "name": "Admin"
        }
    ]
}
```

## Get connected user information [Authenticated]

When your user is authenticated, the password should never be sent again.
Then, use this service to check the token, and extract the information stored inside.
Please pay attention to the "exp" field. This is an UTC timestamp giving you the expiration date of the token.

Past this time, the token is not going to work anymore.

You must be connected to use this service.

```bash
GET http://localhost:5001/api/users/token
```
Result:
```json
{
    "active": true,
    "customer": {
        "id": 2
    },
    "email": "admin",
    "exp": 1535939156,
    "id": 1,
    "name": "admin",
    "roles": [
        {
            "code": "admin",
            "id": 1,
            "name": "Admin"
        }
    ]
}
```

## List users [Authenticated]

This service allows to list user in the database.
You can filter with a LIKE operator on both fields email and name.

You must be connected to use this service. You'll only see the users
from the same customer than your.

```bash
GET http://localhost:5001/api/users/?email=myapp.net&name=admin
```
Result:
```json
{
    "has_next": false,
    "users": [
        {
            "active": true,
            "customer": {
                "id": 1
            },
            "email": "admin",
            "id": 1,
            "name": "admin"
        }
    ]
}
```

## Update a user [Authenticated]

Allows to update a user information.

```bash
PUT http://localhost:5001/api/users/3
```
Payload:
```json
{
	"email": "admin",
	"name": "Admin",
	"password": "password",
	"active": true
}
```
Result:
```json
{
    "active": true,
    "customer": {
        "id": 1
    },
    "email": "admin",
    "id": 1,
    "name": "Admin",
    "roles": [
        {
            "code": "admin",
            "id": 1,
            "name": "Admin"
        }
    ]
}
```
