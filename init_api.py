# coding: utf-8
# This script is used for the first init of the database.

import argparse
import user_api
from user_api import create_user_api
from user_api.db.models import Base, Role, User
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

parser = argparse.ArgumentParser(description=u'Create a user in command line')
parser.add_argument(u'db_url', help=u"The connection URL to the database where to perform operations.")
parser.add_argument(u"jwt_secret", help=u"The JWT secret to generate passwords.")
parser.add_argument(u'admin_password', help=u'The password for the default admin.')
parser.add_argument(u'user_api_sa_password', help=u'The password for the service account.')
args = parser.parse_args()



def init_db():
    engine = create_engine(args.db_url, echo=True)
    conn = engine.connect()
    conn.execution_options(isolation_level="AUTOCOMMIT")
    conn.execute("CREATE DATABASE user_api;")
    conn.close()
    engine = create_engine("{}/{}".format(args.db_url, "user_api", echo=True))
    Base.metadata.create_all(bind=engine)
    conn = engine.connect()
    # conn.execute("CREATE USER 'user_api_sa'@'%' IDENTIFIED BY '{}'".format(
        # args.user_api_sa_password
    # ))
    # conn.execute("REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'user_api_sa'")
    # conn.execute("GRANT ALL PRIVILEGES ON user_api.* TO 'user_api_sa'")
    conn.execute("INSERT INTO customer VALUES(1, NULL);")
    conn.close()


def create_base_users():
    db_url = "{}/{}".format(args.db_url, "user_api")
    engine = create_engine(db_url, echo=True)
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # Create user api object
    user_api = create_user_api(
        db_url=db_url,
        jwt_secret=args.jwt_secret
    )

    # Create Admin user.
    user_api.register(
        1, {
        "email": "admin",
        "name": "admin",
        "active": True,
        "roles": [
            {"id": 1}
        ],
        "password": args.admin_password
    })
    # Fetch created Admin.
    admin = session.query(User).filter_by(email=u"admin").one()
    # Add admin to admin role.
    admin_role = Role(code=u"admin", name=u"Admin")
    admin_role.users.append(admin)
    session.add(admin_role)
    session.commit()

init_db()
create_base_users()
