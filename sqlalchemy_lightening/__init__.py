__author__ = 'dpepper'
__version__ = '0.1.1'


from collections import Iterable
from classproperties import classproperty
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from stringcase import snakecase



class LighteningBase(object):
  @declared_attr
  def __tablename__(cls):
    # generate a default table name, based on class name
    return snakecase(cls.__name__)


  @classproperty
  def query_class(cls):
    '''Override, eg. LighteningBase.query_class = db.session.query'''
    pass


  @classproperty
  def query(cls):
    if not cls.query_class:
      raise NotImplementedError(
        "%s.query or %s.query_class must be set during setup" % (
          cls.__name__,
          cls.__name__,
        )
      )

    return cls.query_class(cls)


  @classproperty
  def all(cls):
    return cls.query.all()


  @classproperty
  def first(cls):
    return cls.query.first()


  @classmethod
  def limit(cls, limit):
    return cls.query.limit(limit)


  @classmethod
  def get(cls, *ids):
    """
    Get a record or records based on their ids
      eg.  Person.get(1)
           Person.get(1, 2)
           Person.get([1, 2])
    """
    assert 1 == len(cls.__table__.primary_key), "compound primary keys not yet supported"

    if len(ids) == 0:
      raise TypeError("id or ids required")

    # eg. get([1, 2, 3])
    iterable = isinstance(ids[0], Iterable) and not isinstance(ids[0], str)
    ids_unpacked = False
    if 1 == len(ids) and iterable:
      ids = ids[0]
      ids_unpacked = True

    if 1 == len(ids):
      # use standard SQLAlchemy
      res = cls.query.get(ids[0])

      if ids_unpacked:
        # repack ids to match input format
        res = [ res ]
    else:
      res = cls.where(id=ids).all()
      if len(ids) != len(res):
        raise ValueError(
          "expected %d values but only got %d" % (len(ids), len(res))
        )


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
    self.query.session.delete(self)
