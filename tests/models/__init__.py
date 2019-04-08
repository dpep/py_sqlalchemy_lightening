import os
import sys

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) ] + sys.path

from sqlalchemy_lightening import LighteningBase, relationship


__all__ = [
    'Person',
    'Pet',
]

@as_declarative()
class BaseModel(LighteningBase):
    id = Column(Integer, primary_key=True)


    def __repr__(self):
      return "%s(%s): %s" % (self.__class__.__name__, self.id, self.name)


class Person(BaseModel):
    name = Column(String(250), nullable=False)
    pets = relationship('Pet')


class Pet(BaseModel):
    name = Column(String(250), nullable=False)
    person_id = Column(Integer, index=True)



engine = create_engine('sqlite:///:memory:')
session = sessionmaker(bind=engine)()

BaseModel.metadata.create_all(engine)
BaseModel.metadata.bind = engine

LighteningBase.query_class = session.query
