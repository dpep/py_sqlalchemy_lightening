__author__ = 'dpepper'
__version__ = '0.5.0'


__all__ = [
  'LighteningBase',
  'relationship',
  'backref',
]


from classproperties import classproperty
from collections import KeysView, ValuesView
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from stringcase import snakecase

import sqlalchemy_lightening.query

from .result_list import ResultList
from .relationship import relationship, backref


class LighteningBase(object):
  @declared_attr
  def __tablename__(cls):
    '''generate a default table name, based on class name'''
    return snakecase(cls.__name__)


  @classproperty
  def query_class(cls):
    '''Override, eg. LighteningBase.query_class = db.session.query'''
    pass


  @classproperty
  def query(cls):
    '''query class specific table'''
    if not cls.query_class:
      raise NotImplementedError(
        "%s.query or %s.query_class must be set during setup" % (
          cls.__name__,
          cls.__name__,
        )
      )

    return cls.query_class(cls)


  @classproperty
  def columns(cls):
    '''list columns'''
    return ResultList(cls.__table__.columns)


  @classproperty
  def all(cls):
    '''retrieve all records'''
    return cls.query.all()


  @classproperty
  def first(cls):
    '''retrieve the first record'''
    return cls.query.first()


  @classmethod
  def limit(cls, limit):
    '''retrieve a specified number of records'''
    return cls.query.limit(limit)


  @classproperty
  def count(cls):
    '''retrieve the total number of records'''
    return cls.query.count()


  @classmethod
  def get(cls, id_or_ids):
    """
    Get a record or records based on it's id
      eg.  Person.get(1)
           Person.get([1, 2])
    """
    assert 1 == len(cls.__table__.primary_key), "compound primary keys not yet supported"
    id_column = list(cls.__table__.primary_key)[0]

    # type cast
    type_cast = id_column.type.python_type

    if isinstance(id_or_ids, (list, set, KeysView, ValuesView)):
      # eg. get([1, 2, 3])
      ids = list(map(type_cast, id_or_ids))
      res = cls.where(**{ id_column.name : ids }).all()
    else:
      # use standard SQLAlchemy
      res = cls.query.get(type_cast(id_or_ids))

    return res


  @classmethod
  def where(cls, *args, **kwargs):
    '''
    Query table, eg.
      Person.where(Person.name == 'dpepper')
      Person.where(name='dpepper')
      Person.where(name=['dpepper', 'josh'])
    '''
    return cls.query.where(*args, **kwargs)


  def save(self):
    self.query.session.add(self)
    return self


  def delete(self):
    self.query.session.delete(self)
