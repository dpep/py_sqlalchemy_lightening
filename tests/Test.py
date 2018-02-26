#!/usr/bin/python

import os
import sys
import unittest

from sqlalchemy.orm.query import Query

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) ] + sys.path

from models import Person


dp = Person(name='dpepper').save()
jp = Person(name='josh').save()


class ArrayTest(unittest.TestCase):
    def test_properties(self):
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



    def test_filter_by(self):
        self.assertIsInstance(Person.filter_by(), Query)

        self.assertEquals(
            dp,
            Person.filter_by(id=1).one()
        )

        self.assertEquals(
            dp,
            Person.filter_by(id=1).one()
        )

        self.assertIsNone(
            Person.filter_by(id=123).one_or_none()
        )

        self.assertEquals(
            dp,
            Person.filter_by(name='dpepper').one()
        )

        self.assertEquals(
            [ dp, jp ],
            Person.filter_by(id=[1, 2]).all()
        )

        self.assertEquals(
            [ dp, jp ],
            Person.filter_by(name=['dpepper', 'josh']).all()
        )


    def test_where(self):
        self.assertIsInstance(Person.where(), Query)

        self.assertEquals(
            [ dp, jp ],
            list(Person.where(id=[1, 2]))
        )

        self.assertEquals(
            [ dp ],
            list(Person.where(Person.id == 1))
        )

        self.assertEquals(
            [ dp, jp ],
            list(Person.where(Person.id.in_([1, 2])))
        )

        self.assertEquals(
            [ dp ],
            Person.where(Person.id == 1, id=1).all()
        )

        self.assertFalse(
            Person.where(Person.id == 1, id=2).all()
        )


    def test_update(self):
        bob = Person(name='bob').save()
        self.assertTrue(Person.where(name='bob').first())

        bob.name = 'bobby'
        bob.save

        self.assertFalse(Person.where(name='bob').first())
        self.assertTrue(Person.where(name='bobby').first())


    def test_delete(self):
        mara = Person(name='mara').save()
        self.assertTrue(Person.where(name='mara').first())
        mara.delete()
        self.assertFalse(Person.where(name='mara').first())


if __name__ == '__main__':
    unittest.main()
