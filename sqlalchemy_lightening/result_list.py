from pluckit import Pluckable
from rekey import Rekeyable


class ResultList(list, Pluckable, Rekeyable):
    def __lshift__(self, other):
        self.append(other)
