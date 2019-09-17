import os
import sys
import unittest

import logging
logging.basicConfig()

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) ] + sys.path

from sqlalchemy_lightening import LighteningBase


__all__ = [
    'BaseModel',
    'TestBase',
]


@as_declarative()
class BaseModel(LighteningBase):
    id = Column(Integer, primary_key=True)


    def __repr__(self):
        if hasattr(self, 'name'):
            return "%s(%s): %s" % (self.__class__.__name__, self.id, self.name)
        return super().__str__()


class TestBase(unittest.TestCase):
    def setUp(self):
        # before each test: reset db, create new session, seed db

        BaseModel.metadata.drop_all()
        BaseModel.metadata.create_all()
        self.session = Session()
        LighteningBase.query_class = self.session.query

        with self.session.begin():
            # seed within transaction to force commit at end
            self.seed()


    def tearDown(self):
        # after each test: clear db
        BaseModel.metadata.drop_all()


    def seed(self):
        pass


engine = create_engine('sqlite:///:memory:')
BaseModel.metadata.bind = engine
Session = sessionmaker(
    bind=engine,
    autocommit=True,
)
session = Session()

# wire things up in case of manual testing
LighteningBase.query_class = session.query
BaseModel.metadata.create_all()
