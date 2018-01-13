# coding: utf-8

import calendar
import datetime
import pytest
from mock import Mock
from pytest import fixture
from user_api.user_api import UserApi
from user_api.user_api_exception import (
    ApiNotFound,
    ApiConflict,
    ApiUnauthorized,
    ApiUnprocessableEntity
)
from user_api.db.db_exception import (
    DBUserNotFound,
    DBUserConflict
)

NOW = datetime.datetime.now()
MOCK_EXPIRATION = int(calendar.timegm(NOW.utctimetuple()))

@fixture(scope=u"function")
def mock_dummy_user():
    return {
        u"id": 3,
        u"email": u"dumb@laposte.net",
        u"name": u"Dummer",
        u"active": 1
    }


@fixture(scope=u"function")
def mock_db_manager(mock_dummy_user):
    mock = Mock()
    mock.get_user_salt = Mock(return_value=u"SALT")
    mock.is_user_hash_valid = Mock(return_value=True)
    mock.get_user_information = Mock(return_value=mock_dummy_user)
    mock.modify_hash_salt = Mock(return_value=None)
    mock.save_new_user = Mock(return_value=mock_dummy_user)
    mock.list_users = Mock(return_value=([mock_dummy_user], False))
    return mock


@fixture(scope=u"function")
def mock_auth_manager(mock_dummy_user):
    mock = Mock()
    mock.generate_salt = Mock(return_value=u"SALT")
    mock.generate_hash = Mock(return_value=u"HASH")
    mock.generate_token = Mock(return_value=u"TOKEN")
    mock_dummy_user[u"exp"] = MOCK_EXPIRATION
    mock.get_token_data = Mock(return_value=mock_dummy_user)
    mock.is_token_valid = Mock(return_value=True)
    return mock


@fixture(scope=u"function")
def stubbed_user_api(mock_db_manager, mock_auth_manager):
    return UserApi(mock_db_manager, mock_auth_manager)


def test_update(stubbed_user_api, mock_dummy_user):
    stubbed_user_api._db_manager.update_user_information = Mock(side_effect=DBUserNotFound)
    mock_dummy_user[u"name"] = u"New name"

    with pytest.raises(ApiNotFound):
        stubbed_user_api.update(mock_dummy_user, mock_dummy_user[u"id"])


def test_authenticate_user(stubbed_user_api, mock_dummy_user):
    payload, token = stubbed_user_api.authenticate(
        mock_dummy_user[u"email"],
        u"1234"
    )
    assert payload == mock_dummy_user
    assert token == token


def test_authenticate_user_not_found(stubbed_user_api, mock_dummy_user):
    stubbed_user_api._db_manager.get_user_salt = Mock(side_effect=DBUserNotFound)
    with pytest.raises(ApiNotFound):
        stubbed_user_api.authenticate(
            mock_dummy_user[u"email"],
            u"1234"
        )


def test_authenticate_invalid_token(stubbed_user_api, mock_dummy_user):
    stubbed_user_api._db_manager.is_user_hash_valid = Mock(return_value=False)
    with pytest.raises(ApiUnauthorized):
        stubbed_user_api.authenticate(
            mock_dummy_user[u"email"],
            u"1234"
        )


def test_reset_password(stubbed_user_api, mock_dummy_user):
    payload = stubbed_user_api.reset_password(
        mock_dummy_user[u"email"],
        u"1234"
    )
    stubbed_user_api._db_manager.modify_hash_salt.assert_called_once_with(
        mock_dummy_user[u"email"], u"HASH", u"SALT"
    )
    assert payload == mock_dummy_user


def test_reset_password_user_not_found(stubbed_user_api, mock_dummy_user):
    stubbed_user_api._db_manager.get_user_information = Mock(side_effect=DBUserNotFound)
    with pytest.raises(ApiUnprocessableEntity):
        payload = stubbed_user_api.reset_password(
            mock_dummy_user[u"email"],
            u"1234"
        )


def test_register(stubbed_user_api, mock_dummy_user):
    user = stubbed_user_api.register(
        mock_dummy_user[u"email"],
        mock_dummy_user[u"name"],
        u"1234"
    )

    assert user == mock_dummy_user


def test_register_conflict(stubbed_user_api, mock_dummy_user):
    stubbed_user_api._db_manager.save_new_user = Mock(side_effect=DBUserConflict)
    with pytest.raises(ApiConflict):
        stubbed_user_api.register(
            mock_dummy_user[u"email"],
            mock_dummy_user[u"name"],
            u"1234"
        )


def test_get_token_data(stubbed_user_api, mock_dummy_user):
    data = stubbed_user_api.get_token_data(u"TOKEN")
    mock_dummy_user.update({
        u"exp": MOCK_EXPIRATION
    })
    assert data == mock_dummy_user


def test_is_token_valid(stubbed_user_api):
    assert stubbed_user_api.is_token_valid(u"TOKEN")
    stubbed_user_api._auth_manager.is_token_valid.assert_called_once_with(u"TOKEN")


def test_list_users(stubbed_user_api, mock_dummy_user):
    assert stubbed_user_api.list_users(10, 5, u"dumb@laposte.net", u"Dummer") == {
        u"users": [
            mock_dummy_user
        ],
        u"has_next": False
    }
    stubbed_user_api._db_manager.list_users.assert_called_once_with(
        10, 5, u"dumb@laposte.net", u"Dummer"
    )


