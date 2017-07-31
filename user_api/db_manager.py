# -*- coding: utf-8 -*-

import logging


class DBManager:

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
        self._db.close()

    def _do_reconnect_if_needed(self, e):
        if e[0] == 2006:
            logging.info(u"Connection lost. Reconnecting ... {}".format(e))
            self._connect()
            logging.info(u"Connection recovered")
        else:
            logging.warning(u"Incident : {}".format(e))
            raise e

    def _execute(self, query, values=None):
        """
        :type query: string
        :param query: The SQL query to execute
        :type values: List
        :param values: The values to sanitize & pass to the query to replace the "%s" values.
        :return:
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

    def get_user_informations(self, email):
        rows, _ = self._execute(u"SELECT id, email, name FROM user WHERE email = %s", (email,))
        if len(rows) == 0:
            return None
        return {
            u"id": rows[0][0],
            u"email": rows[0][1],
            u"name": rows[0][2]
        }

    def get_user_salt(self, email):
        rows, _ = self._execute(u"SELECT salt FROM user WHERE email = %s", (email,))
        if len(rows) == 0:
            return None
        return rows[0][0]

    def modify_hash_salt(self, email, hash, salt):
        """
        :param email:
        :param hash:
        :param salt:
        :return:
        """
        self._execute(
            u"UPDATE user SET hash = %s, salt = %s WHERE email = %s",
            (hash, salt, email)
        )

    def save_new_user(self, email, name, hash, salt):
        try:
            self._execute(
                u"INSERT INTO user(email, name, hash, salt) VALUES (%s, %s, %s, %s);",
                (email, name, hash, salt)
            )
        except self.__db_driver.IntegrityError as e:
            raise ValueError(str(e))

    def is_user_hash_valid(self, email, hash):
        rows, _ = self._execute(u"SELECT hash FROM user WHERE email = %s", (email,))
        if len(rows) == 0:
            return False
        return hash == rows[0][0]
