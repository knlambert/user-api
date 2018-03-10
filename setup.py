
from setuptools import setup

setup(
    name=u'user_api',    # This is the name of your PyPI-package.
    version=u'0.4',                          # Update the version number for new releases
    packages=[
        u'user_api',
        u"user_api.adapter",
        u"user_api.adapter.flask",
        u"user_api.auth",
        u"user_api.db"
    ],
    install_requires=[
        u"ecdsa",
        u'flask',
        u"PyJWT",
        u"sqlalchemy",
        u"cerberus"
    ]
)
