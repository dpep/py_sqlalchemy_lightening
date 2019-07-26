__author__ = 'dpepper'
__version__ = '0.3.3'


__all__ = [
  'LighteningBase',
  'relationship',
]


from collections import Iterable
from classproperties import classproperty
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from stringcase import snakecase

import sqlalchemy_lightening.query

from .result_list import ResultList
from .relationship import relationship


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
  def get(cls, *ids):
    """
    Get a record or records based on their ids
      eg.  Person.get(1)
           Person.get(1, 2)
           Person.get([1, 2])
    """
    assert 1 == len(cls.__table__.primary_key), "compound primary keys not yet supported"
    id_column = list(cls.__table__.primary_key)[0]

    if len(ids) == 0:
      raise ValueError("id or ids required")

    if None in ids:
      raise TypeError("None is an invalid id")

    # eg. get([1, 2, 3])
    ids_unpacked = False
    if 1 == len(ids) and isinstance(ids[0], (list, tuple, set)):
      ids = ids[0]
      ids_unpacked = True

    # type cast
    ids = list(map(id_column.type.python_type, ids))

    if 1 == len(ids):
      # use standard SQLAlchemy
      res = cls.query.get(ids[0])

      if ids_unpacked:
        # repack ids to match input format
        res = ResultList([ res ])
    else:
      res = cls.where(**{ id_column.name : ids }).all()
      if len(ids) != len(res):
        raise ValueError(
          "expected %d values but only got %d" % (len(ids), len(res))
        )

    return res


  @classmethod
  def where(cls, *args, **kwargs):
    '''
    Query table, eg.
      Person.where(Person.name == 'dpepper')
      Person.where(name='dpepper')
      Person.where(name=['dpepper', 'josh'])
    '''
    query = cls.query

    for field, value in kwargs.items():
        column = getattr(cls, field)

        if isinstance(value, (list, tuple, set)):
          query = query.filter(column.in_(value))
        else:
          query = query.filter(column == value)

    if len(args) > 0:
      query = query.filter(*args)

    return query


  def save(self):
    self.query.session.add(self)
    return self


  def delete(self):
    self.query.session.delete(self)
