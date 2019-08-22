# import logging; logging.basicConfig(); logging.getLogger('sqlalchemy_lightening').setLevel(logging.DEBUG)
import os
import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) ] + sys.path

from sqlalchemy_lightening import LighteningBase, relationship


__all__ = [
    'BaseModel',
    'init_db',
    'TestBase',
]

@as_declarative()
class BaseModel(LighteningBase):
    id = Column(Integer, primary_key=True)


    def __repr__(self):
      return "%s(%s): %s" % (self.__class__.__name__, self.id, self.name)


class TestBase(unittest.TestCase):
    def setUp(self):
        init_db()
        self.seed()


    def tearDown(self):
        BaseModel.metadata.drop_all()


    def seed(self):
        pass


engine = create_engine('sqlite:///:memory:')
BaseModel.metadata.bind = engine

def init_db():
    session = sessionmaker(bind=engine)()

    BaseModel.metadata.drop_all()
    BaseModel.metadata.create_all()

    LighteningBase.query_class = session.query


init_db()
