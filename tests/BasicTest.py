#!/usr/bin/python

import os
import sys
import unittest

from sqlalchemy.orm.query import Query

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) ] + sys.path

from models import Person



dp = Person(name='dpepper').save()
jp = Person(name='josh').save()


class BasicTest(unittest.TestCase):
    def test_properties(self):
        self.assertEquals(
            'person',
            Person.__tablename__
        )

        self.assertIsInstance(Person.query, Query)

        self.assertEquals(
            dp,
            Person.first
        )

        self.assertEquals(
            [ dp, jp ],
            Person.all
        )


    def test_get(self):
        self.assertEquals(
            dp,
            Person.get(1)
        )

        self.assertEquals(
            dp,
            Person.get('1')
        )

        self.assertEquals(
            dp,
            Person.get(u'1')
        )

        self.assertEquals(
            [ dp, jp ],
            Person.get(1, 2)
        )

        self.assertEquals(
            [ dp ],
            Person.get([ 1 ])
        )

        self.assertEquals(
            [ dp, jp ],
            Person.get([ 1, 2 ])
        )

        with self.assertRaises(TypeError):
            # missing param
            Person.get()

        with self.assertRaises(Exception):
            # invalid key type
            Person.get([ 1, [ 2 ] ])

        with self.assertRaises(ValueError):
            # missing Person 3
            Person.get(1, 2, 3)



    def test_where(self):
        self.assertIsInstance(Person.where(), Query)

        # args
        self.assertEquals(
            dp,
            Person.where(Person.id == 1).one()
        )

        self.assertEquals(
            dp,
            Person.where(Person.name == 'dpepper').one()
        )

        self.assertEquals(
            [ dp, jp ],
            Person.where(Person.id.in_([1, 2])).all()
        )

        # kwargs
        self.assertEquals(
            dp,
            Person.where(id=1).one()
        )

        self.assertEquals(
            dp,
            Person.where(name='dpepper').one()
        )

        self.assertEquals(
            dp,
            Person.where(name=u'dpepper').one()
        )

        self.assertEquals(
            dp,
            Person.where(id=1, name='dpepper').one()
        )

        self.assertEquals(
            [ dp, jp ],
            Person.where(name=['dpepper', 'josh']).all()
        )

        self.assertIsNone(
            Person.where(id=123).one_or_none()
        )

        self.assertIsNone(
            Person.where(id=2, name='dpepper').one_or_none()
        )

        self.assertEquals(
            [ dp, jp ],
            Person.where(id=[1, 2]).all()
        )

        # args and kwargs
        self.assertEquals(
            dp,
            Person.where(Person.id == 1, id=1).one()
        )

        self.assertIsNone(
            Person.where(Person.id == 1, id=2).one_or_none()
        )

        self.assertEquals(
            dp,
            Person.where(Person.name == 'dpepper', id=[1, 2]).one()
        )


    def test_limit(self):
        self.assertEquals(
            [ dp ],
            list(Person.limit(1))
        )

        self.assertEquals(
            [ dp, jp ],
            list(Person.limit(5))
        )


    def test_count(self):
        self.assertEquals(2, Person.count)


    def test_delete(self):
        mara = Person(name='mara').save()
        self.assertEquals(
            mara,
            Person.where(name='mara').first()
        )
        mara.delete()
        self.assertIsNone(Person.where(name='mara').first())



if __name__ == '__main__':
    unittest.main()
