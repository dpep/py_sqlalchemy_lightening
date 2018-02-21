__author__ = 'dpepper'
__version__ = '0.0.1'


from collections import Iterable
from classproperties import classproperty
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from stringcase import snakecase
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.attributes import QueryableAttribute


class LighteningBase(object):

  def __tablename__(cls):
    # generate a default table name, based on class name
    return snakecase(cls.__name__)


  @classproperty
  def query_class(cls):
    raise NotImplementedError(
      "override during setup: %s.query_class = session.query" % cls.__name__
    )


  @classproperty
  def query(cls):
    return LighteningBase.query_class(cls)


  @classproperty
  def all(cls):
    return cls.query.all()


  @classproperty
  def first(cls):
    return cls.query.first()


  @classmethod
  def get(cls, *id_or_ids):
    """
    Get a record or records based on their ids
      eg.  Person.get(1)
           Person.get(1, 2)
           Person.get([1, 2])
    """
    assert len(id_or_ids) > 0, 'id or ids needed'

    # eg. get([1, 2, 3])
    iterable = isinstance(id_or_ids[0], Iterable) and not isinstance(id_or_ids[0], str)
    if 1 == len(id_or_ids) and iterable:
      id_or_ids = id_or_ids[0]

    res = cls.where(id=id_or_ids)

    if 1 == len(id_or_ids):
      res = res.one_or_none()
    else:
      res = res.all()
      assert len(id_or_ids) == len(res)

    return res


  @classmethod
  def filter_by(cls, **kwargs):
    query = cls.query

    for field, value in kwargs.items():
        column = getattr(cls, field)

        if isinstance(value, Iterable) and not isinstance(value, str):
          query = query.filter(column.in_(value))
        else:
          query = query.filter(column == value)

    return query


  @classmethod
  def where(cls, *args, **kwargs):
    if len(kwargs) > 0:
      query = cls.filter_by(**kwargs)
    else:
      query = cls.query

    if len(args) > 0:
      query = query.filter(*args)

    return query


  def save(self):
    session = self.query.session
    session.add(self)
    return self


  def delete(self):
    session = self.query.session
    session.delete(self)
