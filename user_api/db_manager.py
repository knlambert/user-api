# -*- coding: utf-8 -*-
"""
Contains the DB manager.
"""
import logging


class DBManager:
    """
    Handles the interactions with the database.
    """

    def __init__(
            self,
            db_driver,
            db_user,
            db_passwd,
            db_name,
            db_host=None,
            db_unix_socket=None
    ):
        self.__db_driver = db_driver
        self._db_host = db_host
        self._db_unix_socket = db_unix_socket
        self._db_user = db_user
        self._db_passwd = db_passwd
        self._db_name = db_name
        self._db = None

    def _connect(self):
        """
        Connect to the database.
        """
        params = {
            u"user": self._db_user,
            u"passwd": self._db_passwd,
            u"db": self._db_name,
            u"charset": u"utf8"
        }
        if self._db_host:
            params[u"host"] = self._db_host
        else:
            params[u"unix_socket"] = self._db_unix_socket
        self._db = self.__db_driver.connect(**params)

    def _disconnect(self):
        """
        Disconnect from the database.
        """
        self._db.close()

    def _do_reconnect_if_needed(self, e):
        """
        Reconnect if connection lost.
        Args:
            e: Th exception to test.

        """
        if e[0] == 2006:
            logging.info(u"Connection lost. Reconnecting ... {}".format(e))
            self._connect()
            logging.info(u"Connection recovered")
        else:
            logging.warning(u"Incident : {}".format(e))
            raise e

    def _execute(self, query, values=None):
        """
        Execute a SQL Query.
        Args:
            query (unicode): The query to execute.
            values (list): A list of values to insert in the query.

        Returns:
            (tuple): A tuple result / description.
        """
        self._connect()
        cursor = self._db.cursor()
        try:
            cursor.execute(query, values)
        except self.__db_driver.OperationalError as e:
            self._do_reconnect_if_needed(e)
            cursor.execute(query, values)

        self._db.commit()
        self._disconnect()
        return cursor.fetchall(), cursor.description

    def get_user_information(self, email):
        """
        Get the information of the user from his email.
        Args:
            email (unicode): The email of the user we want the information.

        Returns:
            (dict): The user information.
        """
        rows, _ = self._execute(u"SELECT id, email, name FROM user WHERE email = %s", (email,))
        if len(rows) == 0:
            return None
        return {
            u"id": rows[0][0],
            u"email": rows[0][1],
            u"name": rows[0][2]
        }

    def get_user_salt(self, email):
        """
        Get the salt for the user.
        Args:
            email (unicode): The email of the user we want the salt.

        Returns:
            (unicode): The salt.
        """
        rows, _ = self._execute(u"SELECT salt FROM user WHERE email = %s", (email,))
        if len(rows) == 0:
            return None
        return rows[0][0]

    def modify_hash_salt(self, email, hash, salt):
        """
        Modify the hash / salt for a specific user (email).
        Args:
            email (unicode): The email of the user to alter.
            hash (unicode): The hash (password).
            salt (unicode): The salt associated with the hash before saving.
        """
        self._execute(
            u"UPDATE user SET hash = %s, salt = %s WHERE email = %s",
            (hash, salt, email)
        )

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
            self._execute(
                u"INSERT INTO user(email, name, hash, salt) VALUES (%s, %s, %s, %s);",
                (email, name, hash, salt)
            )
        except self.__db_driver.IntegrityError as e:
            raise ValueError(str(e))

    def is_user_hash_valid(self, email, hash):
        """
        Check if a hash is valid.
        Args:
            email (unicode): The email of the user we are checking the hash.
            hash (unicode): The hash to test.

        Returns:
            (boolean): If the hash is valid or not.
        """
        rows, _ = self._execute(u"SELECT hash FROM user WHERE email = %s", (email,))
        if len(rows) == 0:
            return False
        return hash == rows[0][0]
