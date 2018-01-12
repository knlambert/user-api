# coding: utf-8

from .db_manager import DBManager
from .authentication import Authentication
from .adapter.flask_adapter import FlaskAdapter


class UserApi(object):

    def __init__(
        self,
        db_manager,
        authentication
    ):
        """
        Build the user API
        Args:
            db_manager (DBManager): Injected object to handle DB interaction.
            authentication (Authentication): Injected object to handle Auth interactions.
        """
        self.db_manager = db_manager
        self.authentication = authentication

    def get_flask_adapter(self):
        """
        Get an adapter for the API.

        Returns:
            (FlaskAdapter): The adapter.
        """
        return FlaskAdapter(self.db_manager, self.authentication)


