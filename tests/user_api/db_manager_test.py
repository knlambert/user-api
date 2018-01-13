# coding: utf-8

from mock import Mock
from pytest import fixture
from user_api.db.db_manager import DBManager


@fixture(scope=u"function")
def stubbed_db_manager():
    return DBManager(
        db_driver=Mock(),
        db_user=u"root",
        db_passwd=u"localroot1234",
        db_name=u"user_api",
        db_host=u"127.0.0.1"
    )


def test_list_users_standard(stubbed_db_manager):
    stubbed_db_manager._execute = Mock(
        return_value=([
            [i, u"dummy{}@gmail.com".format(i), u"dumb{}".format(i)]
            for i in range(0, 6)
        ], None)
    )

    result = stubbed_db_manager.list_users(
        5,
        0,
        u"dummy",
        u"dumb"
    )

    stubbed_db_manager._execute.assert_called_once_with(
        query=u"SELECT id, email, name FROM user "
              u"WHERE email LIKE %s AND name LIKE %s "
              u"LIMIT %s OFFSET %s",
        values=[u"%dummy%", u"%dumb%", 6, 0]
    )
    assert result == {
        u"users": [
            {
                u"id": i,
                u"email": u"dummy{}@gmail.com".format(i),
                u"name": u"dumb{}".format(i)
            }
            for i in range(0, 5)
        ],
        u"has_next": True
    }


def test_list_users_empty(stubbed_db_manager):
    stubbed_db_manager._execute = Mock(
        return_value=([], None)
    )

    result = stubbed_db_manager.list_users(
        20,
        0
    )

    stubbed_db_manager._execute.assert_called_once_with(
        query=u"SELECT id, email, name FROM user  "
              u"LIMIT %s OFFSET %s",

        values=[21, 0]
    )
    assert result == {
        u"users": [],
        u"has_next": False
    }
