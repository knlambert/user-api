
from setuptools import setup

setup(
    name=u'user_api',    # This is the name of your PyPI-package.
    version=u'0.3',                          # Update the version number for new releases
    packages=[
        u'user_api',
        u"user_api.adapter"
    ],
    install_requires=[
        u"ecdsa",
        u'flask',
        u"PyJWT",
        u"sqlalchemy",
        u"cerberus"
    ]
)
