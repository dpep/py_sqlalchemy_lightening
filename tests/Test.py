#!/usr/bin/python

import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')) ] + sys.path

from models import Person


dp = Person(name='dpepper').save()
jp = Person(name='josh').save()


class ArrayTest(unittest.TestCase):
    def test_basics(self):
        self.assertEquals(
            dp,
            Person.get(1)
        )

        self.assertEquals(
            dp,
            Person.first
        )

        self.assertEquals(
            2,
            len(Person.all)
        )


    def test_filter_by(self):
        self.assertEquals(
            [ dp ],
            list(Person.filter_by(id=1))
        )

        self.assertEquals(
            [ dp, jp ],
            list(Person.filter_by(id=[1, 2]))
        )


    def test_where(self):
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

        self.assertTrue(
            Person.where(name='bob').first()
        )

        bob.name = 'bobby'
        bob.save

        self.assertFalse(
            Person.where(name='bob').first()
        )

        self.assertTrue(
            Person.where(name='bobby').first()
        )




if __name__ == '__main__':
    unittest.main()
