
from setuptools import setup

setup(
    name="user_api", 
    version="0.6.0",   
    packages=[
        "user_api",
        "user_api.adapter",
        "user_api.adapter.flask",
        "user_api.auth",
        "user_api.db"
    ],
    install_requires=[
        "ecdsa==0.13.3",
        "flask>=1.0.2,<2",
        "PyJWT>=1.6.4,<2",
        "SQLAlchemy>=1.2,<2",
        "Cerberus>=1.2,<2",
        "pycryptodome>=3.6,<4",
        "mysql-connector>=2.1.6,<3"
    ]
)
