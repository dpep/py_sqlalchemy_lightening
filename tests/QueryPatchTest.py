#!/usr/bin/env python

import os
import sys
import unittest

from sqlalchemy import Column, String

sys.path = [ os.path.abspath(os.path.dirname(__file__)) ] + sys.path

from support import BaseModel, TestBase


class Student(BaseModel):
    name = Column(String)


class QueryPatchTest(TestBase):
    def seed(self):
        Student(name='dpepper').save()
        Student(name='josh').save()


    def test_pluck(self):
        self.assertEqual(
            ['dpepper', 'josh'],
            Student.query.all().pluck('name')
        )

        self.assertEqual(
            ['dpepper', 'josh'],
            Student.query.pluck('name')
        )

        self.assertEqual(
            ['dpepper'],
            Student.query.limit(1).pluck('name')
        )

        self.assertEqual(
            ['dpepper'],
            Student.query.filter(Student.name == 'dpepper').pluck('name')
        )


    def test_pluck_lightening(self):
        self.assertEqual(
            ['dpepper', 'josh'],
            Student.all.pluck('name')
        )

        self.assertEqual(
            ['dpepper'],
            Student.limit(1).pluck('name')
        )

        self.assertEqual(
            ['dpepper'],
            Student.where(name='dpepper').pluck('name')
        )

        with self.assertRaises(AttributeError):
            Student.get(1).pluck('name')

        self.assertEqual(
            ['dpepper'],
            Student.get([ 1 ]).pluck('name')
        )

        self.assertEqual(
            ['dpepper', 'josh'],
            Student.get(1, 2).pluck('name')
        )


    def test_rekey(self):
        self.assertEqual(
            { 1 : 'dpepper', 2 : 'josh' },
            Student.query.all().rekey('id', 'name')
        )

        self.assertEqual(
            { 1 : 'dpepper', 2 : 'josh' },
            Student.query.rekey('id', 'name')
        )


    def test_rekey_lightening(self):
        self.assertEqual(
            { 1 : 'dpepper', 2 : 'josh' },
            Student.all.rekey('id', 'name')
        )

        self.assertEqual(
            { 1 : 'dpepper' },
            Student.where(name='dpepper').rekey('id', 'name')
        )

        self.assertEqual(
            { 1 : 'dpepper' },
            Student.where(name=['dpepper', 'josh']).limit(1).rekey('id', 'name')
        )



if __name__ == '__main__':
    unittest.main()
