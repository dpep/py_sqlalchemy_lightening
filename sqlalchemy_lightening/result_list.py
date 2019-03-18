from pluckit import Pluckable
from rekey import Rekeyable


class ResultList(list, Pluckable, Rekeyable): pass
