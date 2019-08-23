import os
import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) ] + sys.path

from sqlalchemy_lightening import LighteningBase


__all__ = [
    'BaseModel',
    'init_db',
    'TestBase',
]


@as_declarative()
class BaseModel(LighteningBase):
    id = Column(Integer, primary_key=True)


    def __str__(self):
        if hasattr(self, 'name'):
            return "%s(%s): %s" % (self.__class__.__name__, self.id, self.name)
        return super().__str__()


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
Session = sessionmaker(
    bind=engine,
    autocommit=True,
)

def init_db():
    BaseModel.metadata.drop_all()
    BaseModel.metadata.create_all()

    # create new session
    LighteningBase.query_class = Session().query


init_db()
