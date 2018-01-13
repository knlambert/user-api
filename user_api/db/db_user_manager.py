# -*- coding: utf-8 -*-
"""
Contains the DB manager.
"""

from .db_exception import (
    DBUserConflict,
    DBUserNotFound
)
from .models import User
from sqlalchemy import exc
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, load_only, exc as orm_exc


class DBUserManager:
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
        self._engine = create_engine(url)

    def get_session(self):
        """
        Returns a DB access session.
        Returns:
            (Session): The session object.
        """
        session = sessionmaker(self._engine)
        return session()

    @staticmethod
    def to_user_dict(user):
        """
        Take a user Object to transform it into dict.
        Args:
            user (User): The user to process.
        Returns:
            (dict): The user.

        """
        return {
            col: getattr(user, col)
            for col in [u"id", u"email", u"name", u"active"]
        }

    def get_user_information(self, user_id):
        """
        Get the information of the user from his email.
        Args:
            user_id (unicode): The email of the user we want the information.

        Returns:
            (dict): The user information.
        """
        filters = {}
        try:
            filters[u"id"] = int(user_id)
        except ValueError:
            filters[u"email"] = user_id

        session = self.get_session()
        columns = [u"id", u"email", u"name", u"active"]

        try:
            user = session.query(User).filter_by(**filters).options(load_only(*columns)).one()
        except orm_exc.NoResultFound:
            return DBUserNotFound

        return self.to_user_dict(user)

    def update_user_information(self, email, name, active, user_id):
        """
        Update information for a user.
        Args:
            email (unicode): The updated email for the user.
            name (unicode): The updated name for the user.
            active (boolean): The updated status for the use.
            user_id (int): The ID of the user to update.

        Returns:
            (dict): The updated user.
        """
        session = self.get_session()
        try:
            session.query(User)\
                .filter_by(id=user_id)\
                .update({
                    u"email": email,
                    u"name": name,
                    u"active": active
                })
        except exc.IntegrityError:
            raise DBUserConflict

        session.commit()
        return self.get_user_information(user_id)

    def get_user_salt(self, email):
        """
        Get the salt for the user.
        Args:
            email (unicode): The email of the user we want the salt.

        Returns:
            (unicode): The salt.
        """
        session = self.get_session()
        try:
            user = session.query(User).filter_by(email=email).options(load_only(u"salt")).one()

        except orm_exc.NoResultFound:
            raise DBUserNotFound

        return user.salt

    def modify_hash_salt(self, email, hash, salt):
        """
        Modify the hash / salt for a specific user (email).
        Args:
            email (unicode): The email of the user to alter.
            hash (unicode): The hash (password).
            salt (unicode): The salt associated with the hash before saving.
        """
        session = self.get_session()
        session.query(User)\
            .filter_by(email=email)\
            .update({User.hash: hash, User.salt: salt})

        session.commit()

    def save_new_user(self, email, name, hash, salt):
        """
        Save a new user.
        Args:
            email (unicode): The email of the user to save.
            name (unicode): The name of the user.
            hash (unicode): The hash (password).
            salt (unicode): The salt associated with the hash before saving.

        Raises:
            (ValueError): if user breaks a constraint.
        """
        try:
            session = self.get_session()
            user = User(
                email=email,
                name=name,
                hash=hash,
                salt=salt
            )
            session.add(user)
            session.commit()
            return {
                u"id": user.id,
                u"email": user.email,
                u"name": user.name,
                u"active": user.active
            }

        except exc.IntegrityError as err:
            raise DBUserConflict

    def is_user_hash_valid(self, email, hash):
        """
        Check if a hash is valid.
        Args:
            email (unicode): The email of the user we are checking the hash.
            hash (unicode): The hash to test.

        Returns:
            (boolean): If the hash is valid or not.
        """
        session = self.get_session()
        user = session.query(User).filter_by(email=email).options(load_only(u"hash")).one()

        return False if (user is None or hash != user.hash) else True

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
        session = self.get_session()
        columns = [u"id", u"email", u"name", u"active"]

        filters = []
        if email is not None:
            filters.append(User.email.like(u"%{}%".format(email)))

        if name is not None:
            filters.append(User.name.like(u"%{}%".format(name)))

        users = session.query(User)\
            .options(load_only(*columns))\
            .filter(and_(*filters))\
            .offset(offset)\
            .limit(limit+1)

        if users.count() > limit:
            users = users[:-1]
            has_next = True
        else:
            has_next = False

        return [
            {
                u"id": user.id,
                u"email": user.email,
                u"name": user.name,
                u"active": user.active
            }
            for user in users
        ], has_next

