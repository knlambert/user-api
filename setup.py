
from setuptools import setup

setup(
    name=u'user_api',    # This is the name of your PyPI-package.
    version=u'0.4.1',                          # Update the version number for new releases
    packages=[
        u'user_api',
        u"user_api.adapter",
        u"user_api.adapter.flask",
        u"user_api.auth",
        u"user_api.db"
    ],
    install_requires=[
        u"ecdsa==0.13",
        u'flask>=1.0.2,<2',
        u"PyJWT>=1.6.4,<2",
        u'SQLAlchemy>=1.2,<2',
        u"Cerberus>=1.2,<2",
        u"pycrypto>=2.6.1,<3"
    ]
)
