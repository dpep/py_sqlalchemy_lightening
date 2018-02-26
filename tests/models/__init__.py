from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_lightening import LighteningBase

Base = declarative_base()



class Person(LighteningBase, Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


    def __repr__(self):
      return "%s: %s" % (self.__class__.__name__, self.name)




engine = create_engine('sqlite:///:memory:')
session = sessionmaker(bind=engine)()

Base.metadata.create_all(engine)
Base.metadata.bind = engine

LighteningBase.query_class = session.query
