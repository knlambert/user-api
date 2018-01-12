# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):

    __tablename__ = u"user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True)
    name = Column(String(255))
    hash = Column(String(255))
    salt = Column(String(255))
