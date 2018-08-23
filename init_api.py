# coding: utf-8
# This script is used for the first init of the database.

import argparse
import user_api
from user_api.helpers import init_db, add_user

parser = argparse.ArgumentParser(description=u'Init the API.')
parser.add_argument(u'db_url', help=u"The connection URL to the database where to perform operations.")
parser.add_argument(u"jwt_secret", help=u"The JWT secret to generate passwords.")
parser.add_argument(u'admin_password', help=u'The password for the default admin.')
parser.add_argument(u'--drop-before', action='store_true', default=False, help='Do drop the database if it already exists.')
args = parser.parse_args()

init_db(db_url=args.db_url, drop_before=args.drop_before)
add_user(
    db_url=args.db_url, 
    jwt_secret=args.jwt_secret,
    username="admin",
    email="admin",
    password=args.admin_password
)

