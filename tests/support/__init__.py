import unittest

import logging
logging.basicConfig()

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer
from sqlalchemy.orm import as_declarative
from sqlalchemy.orm import sessionmaker

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
        return super().__repr__()


engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)


class TestBase(unittest.TestCase):
    def setUp(self):
        # before each test: reset db, create new session, seed db
        BaseModel.metadata.drop_all(engine)
        BaseModel.metadata.create_all(engine)

        self.session = Session()
        LighteningBase.query_class = self.session.query

        self.seed()
        self.session.commit()


    def tearDown(self):
        # after each test: clear db
        self.session.close()
        BaseModel.metadata.drop_all(engine)


    def seed(self):
        pass


# wire things up in case of manual testing
session = Session()
LighteningBase.query_class = session.query
BaseModel.metadata.create_all(engine)
