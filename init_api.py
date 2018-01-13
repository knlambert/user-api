# coding: utf-8

import argparse
from user_api import create_user_api
from user_api.db.models import Base, Role, User
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

parser = argparse.ArgumentParser(description=u'Create a user in command line')
parser.add_argument(u'db_url', help=u"The connection URL to the database where to perform operations.")
parser.add_argument(u"jwt_secret", help=u"The JWT secret to generate passwords.")
parser.add_argument(u'admin_password', help=u'The password for the default admin.')

args = parser.parse_args()

engine = create_engine(args.db_url, echo=True)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Create user api object
user_api = create_user_api(
    db_url=args.db_url,
    jwt_secret=args.jwt_secret
)


def init_db():
    Base.metadata.create_all(bind=engine)


def create_base_users():
    # Create Admin user.
    user_api.register(u"admin", u"Admin", args.admin_password)
    # Fetch created Admin.
    admin = session.query(User).filter_by(email=u"admin").one()
    # Add admin to admin role.
    admin_role = Role(code=u"admin", name=u"Admin")
    admin_role.users.append(admin)
    session.add(admin_role)
    session.commit()

init_db()
create_base_users()
