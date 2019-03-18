from pluckit import pluck
from rekey import rekey
from sqlalchemy.orm.query import Query

from .result_list import ResultList


def patch_query():
    # monkey patch SQLAlchemy Query object
    Query.pluck = lambda self, handle: pluck(self, handle)
    Query.rekey = lambda self, key, handle: rekey(self, key, handle)

    # all() should return a pluckable/rekeyable
    Query.__sa_all = Query.all
    Query.all = lambda self: ResultList(self.__sa_all())
