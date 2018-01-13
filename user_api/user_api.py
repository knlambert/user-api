# coding: utf-8

from .db.db_user_manager import DBUserManager
from .db.db_exception import (
    DBUserConflict,
    DBUserNotFound
)
from user_api_exception import (
    ApiConflict,
    ApiNotFound,
    ApiForbidden,
    ApiUnauthorized,
    ApiUnprocessableEntity
)
from .auth.auth_manager import AuthManager
from .adapter.flask_adapter import FlaskAdapter


class UserApi(object):

    def __init__(
        self,
        db_user_manager,
        db_role_manager,
        auth_manager
    ):
        """
        Build the user API
        Args:
            db_user_manager (DBUserManager): Injected object to handle DB interaction.
            db_group_manager (DBRoleManager): Injected object to handle DB interaction.
            auth_manager (AuthManager): Injected object to handle Auth interactions.
        """
        self._db_user_manager = db_user_manager
        self._db_role_manager = db_role_manager
        self._auth_manager = auth_manager

    def get_flask_adapter(self):
        """
        Get an adapter for the API.

        Returns:
            (FlaskAdapter): The adapter.
        """
        return FlaskAdapter(self)

    def update(self, payload, user_id):
        """
        Update a user.
        Args:
            payload (dict): The user to update.
            user_id (int): The ID of the user to update.

        Returns:
            (dict): The updated user.
        """
        try:
            payload[u"user_id"] = user_id
            user = self._db_user_manager.update_user_information(**payload)
            return user
        except DBUserConflict:
            raise ApiConflict
        except DBUserNotFound:
            raise ApiNotFound(u"User not found.")

    def authenticate(self, email, password):
        """
        Authenticate a user.
        Args:
            email (unicode): The user email.
            password (unicode): The user password.

        Returns:
            (dict): The user auth information.
        """
        try:
            salt = self._db_user_manager.get_user_salt(email=email)
        except DBUserNotFound:
            raise ApiNotFound(u"Can't find user {}.".format(email))

        hash = self._auth_manager.generate_hash(
            password,
            salt
        )
        valid = self._db_user_manager.is_user_hash_valid(
            email,
            hash=hash
        )
        if not valid:
            raise ApiUnauthorized(u"Wrong login or / and password.")

        payload = self._db_user_manager.get_user_information(email)
        if not payload[u"active"]:
            raise ApiUnauthorized(u"User is not active.")

        payload[u"roles"] = self._db_role_manager.get_user_roles(
            user_id=payload[u"id"]
        )
        token = self._auth_manager.generate_token(payload)
        return payload, token

    def reset_password(self, email, password):
        """
        Reset a user password.
        Args:
            email (unicode): The user email.
            password (unicode): The user new password.

        Returns:
            (dict): The user auth new information.
        """
        salt = self._auth_manager.generate_salt()
        hash = self._auth_manager.generate_hash(password, salt)

        self._db_user_manager.modify_hash_salt(email, hash, salt)
        try:
            payload = self._db_user_manager.get_user_information(email)
        except DBUserNotFound:
            raise ApiUnprocessableEntity(u"User '{}' doesn't exist.".format(email))

        return payload

    def register(self, email, name, password):
        """
        Register a new user.
        Args:
            email (unicode): The user email.
            name (unicode): The user name.
            password (unicode): The user password.

        Returns:
            (dict): The user auth new information.
        """
        salt = self._auth_manager.generate_salt()
        hash = self._auth_manager.generate_hash(password, salt)
        try:
            user = self._db_user_manager.save_new_user(
                email=email,
                name=name,
                hash=hash,
                salt=salt
            )
            return user
        except DBUserConflict:
            raise ApiConflict(u"User already exists.")

    def get_token_data(self, token):
        """
        Decrypt token and return payload.
        Args:
            token (unicode): The JWT token.

        Returns:
            (dict): The payload contained in the token.
        """
        return self._auth_manager.get_token_data(token)

    def is_token_valid(self, token):
        """
        Check if a token is valid.
        Args:
            token (unicode): The token value.

        Returns:
            (boolean): Return True if valid, else False.
        """
        return self._auth_manager.is_token_valid(token)

    def list_users(self, limit=20, offset=0, email=None, name=None):
        """
        List the users from the API.
        Args:
            limit (int): The max number of returned users.
            offset (int): The cursor.
            email (unicode): An email to filter on.
            name (unicode): A name to filter on.

        Returns:
            (list of dict, boolean): A list of user representations. The boolean stands for if there is more to fetch.
        """
        users, has_next = self._db_user_manager.list_users(limit, offset, email, name)
        return {
            u"users": users,
            u"has_next": has_next
        }

    def token_has_roles(self, token, roles):
        """
        Check if a token is authorized for a role list.
        Args:
            token (unicode): The token to check.
            roles (list of unicode): The list of roles code to check.

        Returns:
            (boolean): Returns true if it has the roles.

        Raises
            (ApiForbidden): Raised if the token doesn't have the expected roles.
        """
        token = self._auth_manager.get_token_data(token)
        missing_roles = []
        user_roles = [role[u"code"] for role in token[u"roles"]]
        for required_role in roles:
            if required_role not in user_roles:
                missing_roles.append(required_role)
        if len(missing_roles) > 0:
            raise ApiForbidden(u"You don't have the {} role(s).".format(u", ".join(missing_roles)))

        return True