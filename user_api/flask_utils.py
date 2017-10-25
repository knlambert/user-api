# coding: utf-8

from functools import wraps
from cerberus import Validator
from flask import jsonify, request


def flask_constructor_error(message, status=500, custom_error_code=None, error_payload=None):
    """
    Construct Json Error returned message.
    """
    payload = {
        u"message": message
    }
    if error_payload:
        payload[u"payload"] = error_payload

    if custom_error_code:
        payload[u"error_code"] = custom_error_code

    return jsonify(payload), status


def flask_construct_response(item, code=200):
    """
    Construct Json response returned.
    """
    return jsonify(item), code


def flask_check_args(validation_schema):
    """

    Args:
        validation_schema (dict):

    Returns:
        (funct):
    """

    def decorated(funct):
        @wraps(funct)
        def wrapper(*args, **kwargs):
            args_dict = request.args.copy().to_dict()

            validator = Validator(validation_schema)
            # Check if the document is valid.
            if not validator.validate(args_dict):
                return flask_constructor_error(
                    message=u"Wrong args.",
                    custom_error_code=u"WRONG_ARGS",
                    status=422,
                    error_payload=validator.errors
                )

            kwargs[u"args"] = validator.document
            return funct(*args, **kwargs)

        return wrapper

    return decorated