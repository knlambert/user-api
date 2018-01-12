# -*- coding: utf-8 -*-
"""
Contains the DB manager.
"""

import logging
from .models import User
from sqlalchemy import exc
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, load_only


class DBManager:
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

    def get_user_information(self, email):
        """
        Get the information of the user from his email.
        Args:
            email (unicode): The email of the user we want the information.

        Returns:
            (dict): The user information.
        """
        session = self.get_session()
        columns = [u"id", u"email", u"name"]
        user = session.query(User).filter_by(email=email).options(load_only(*columns)).one()

        if user is None:
            return None

        return {
            col: getattr(user, col)
            for col in columns
        }

    def get_user_salt(self, email):
        """
        Get the salt for the user.
        Args:
            email (unicode): The email of the user we want the salt.

        Returns:
            (unicode): The salt.
        """
        session = self.get_session()
        user = session.query(User).filter_by(email=email).options(load_only(u"salt")).one()
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

        except exc.IntegrityError as err:
            raise ValueError(unicode(err))

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
        columns = [u"id", u"email", u"name"]

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

        return {
            u"users": [
                {
                    u"id": user.id,
                    u"email": user.email,
                    u"name": user.name
                }
                for user in users
            ],
            u"has_next": has_next
        }

