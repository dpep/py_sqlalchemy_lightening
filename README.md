SQLAlchemy Lightening
===
Making SQLAlchemy great again


#### Install
```pip install sqlalchemy_ligthening```


#### Usage
```
# load by id
Person.get(1)

# load multiple by id
Person.get(1, 2, 3)
# or
Person.get([1, 2, 3])

# basic filter
Person.where(name='dpepper')

# where `name` in ...
Person.where(name=['dpepper', 'thatguy'])

# mix and match
Person.where(Person.id != 1, name='dpepper')

# standard utilities
Person.all
Person.first

# standard SQLAlchemy query
Person.query
```

##  Example Setup
```
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_lightening import LighteningBase


# create base sqlalchemy model
Base = declarative_base()

# extend LighteningBase mixin
class Person(LighteningBase, Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(250))

engine = create_engine('sqlite:///:memory:')
session = sessionmaker(bind=engine)()

Base.metadata.create_all(engine)
Base.metadata.bind = engine

# wire things up
LighteningBase.query_class = session.query

# good to go
Person.winning
```


----
[![installs](https://img.shields.io/pypi/dm/sqlalchemy_lightening.svg?label=installs)](https://pypi.org/project/sqlalchemy_lightening)
