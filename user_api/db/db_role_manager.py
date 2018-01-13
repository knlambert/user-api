# -*- coding: utf-8 -*-
"""
Contains the DB Role manager.
"""

from .models import Role, User
from .db_manager import DBManager
from sqlalchemy.orm import joinedload


class DBRoleManager(DBManager):
    """
    Handles the interactions with the database.
    """

    def __init__(
            self,
            url
    ):
        """
        Constructor.
        Args:
            url (unicode): The construction URL to connect to the database.
        """
        DBManager.__init__(self, url)

    @staticmethod
    def to_role_dict(role):
        """
        Take a role Object to transform it into dict.
        Args:
            role (Role): The role to process.
        Returns:
            (dict): The role.

        """
        return {
            col: getattr(role, col)
            for col in [u"id", u"code", u"name"]
        }

    def get_user_roles(self, user_id):
        """
        Get the list of roles for a specific user.
        Args:
            user_id (int): The ID of the user we want the roles.
        Returns:
            (list of dict): The list of roles.
        """
        session = self.get_session()
        user = session.query(User) \
            .filter_by(id=user_id) \
            .options(joinedload(u"roles"))\
            .one()
        return [
            self.to_role_dict(role) for role in user.roles
        ]
