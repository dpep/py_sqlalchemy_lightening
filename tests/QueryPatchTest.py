#!/usr/bin/env python

import os
import sys
import unittest

from sqlalchemy.orm.query import Query

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '.')) ] + sys.path

from models import Person


Person.query.delete()
dp = Person(name='dpepper').save()
jp = Person(name='josh').save()


class QueryPatchTest(unittest.TestCase):

    def test_pluck(self):
        self.assertEqual(
            ['dpepper', 'josh'],
            Person.query.all().pluck('name')
        )

        self.assertEqual(
            ['dpepper', 'josh'],
            Person.query.pluck('name')
        )

        self.assertEqual(
            ['dpepper'],
            Person.query.limit(1).pluck('name')
        )

        self.assertEqual(
            ['dpepper'],
            Person.query.filter(Person.name == 'dpepper').pluck('name')
        )


    def test_pluck_lightening(self):
        self.assertEqual(
            ['dpepper', 'josh'],
            Person.all.pluck('name')
        )

        self.assertEqual(
            ['dpepper'],
            Person.limit(1).pluck('name')
        )

        self.assertEqual(
            ['dpepper'],
            Person.where(name='dpepper').pluck('name')
        )

        with self.assertRaises(AttributeError):
            Person.get(1).pluck('name')

        self.assertEqual(
            ['dpepper'],
            Person.get([ 1 ]).pluck('name')
        )

        self.assertEqual(
            ['dpepper', 'josh'],
            Person.get(1, 2).pluck('name')
        )


    def test_rekey(self):
        self.assertEqual(
            { 1 : 'dpepper', 2 : 'josh' },
            Person.query.all().rekey('id', 'name')
        )

        self.assertEqual(
            { 1 : 'dpepper', 2 : 'josh' },
            Person.query.rekey('id', 'name')
        )


    def test_rekey_lightening(self):
        self.assertEqual(
            { 1 : 'dpepper', 2 : 'josh' },
            Person.all.rekey('id', 'name')
        )

        self.assertEqual(
            { 1 : 'dpepper' },
            Person.where(name='dpepper').rekey('id', 'name')
        )

        self.assertEqual(
            { 1 : 'dpepper' },
            Person.where(name=['dpepper', 'josh']).limit(1).rekey('id', 'name')
        )



if __name__ == '__main__':
    unittest.main()
