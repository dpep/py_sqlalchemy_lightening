from pluckit import pluck
from rekey import rekey
from sqlalchemy.orm.query import Query

from .result_list import ResultList


# monkey patch SQLAlchemy Query object
Query.pluck = lambda self, handle: pluck(self, handle)
Query.rekey = lambda self, key, handle: rekey(self, key, handle)

# all() should return a pluckable/rekeyable
Query.__sa_all = Query.all
Query.all = lambda self: ResultList(self.__sa_all())


def where(self, *args, **kwargs):
    query = self
    columns = self._entities[0].entity_zero.columns

    for field, value in kwargs.items():
        column = columns[field]

        if isinstance(value, (list, tuple, set)):
          query = query.filter(column.in_(value))
        else:
          query = query.filter(column == value)

    if len(args) > 0:
        query = query.filter(*args)

    return query

Query.where = where
