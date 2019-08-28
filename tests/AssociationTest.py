#!/usr/bin/env python

import os
import sys
import unittest

from sqlalchemy import *
from sqlalchemy.orm.interfaces import MANYTOMANY

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '.')) ] + sys.path

from support import BaseModel, TestBase
from sqlalchemy_lightening.association import association, init_assocs, Association


init_assocs(BaseModel)

class Company(BaseModel):
    name = Column(String)
    employees = association('Employee')
    ceo = association('Employee', uselist=False, single_parent=True, cascade='all, delete-orphan')
    mvp = association('Employee', type='favorite', uselist=False)


class Employee(BaseModel):
    name = Column(String)


class AssociationTest(TestBase):
    def seed(self):
        global ww, dp, amol, jarah, eng
        ww = Company(name='WorkWhile').save()
        dp = Employee(name='dpepper').save()
        amol = Employee(name='amol').save()
        jarah = Employee(name='jarah').save()


    def test_assoc(self):
        self.assertEqual(0, Association.count)
        self.assertEqual([], ww.employees)

        ww.employees << dp
        self.assertEqual([ dp ], ww.employees)
        self.assertEqual(1, Association.count)

        ww.employees.append(amol)
        self.assertEqual([ dp, amol ], ww.employees)
        self.assertEqual(2, Association.count)


        # test deletion
        ww.employees.remove(dp)
        self.assertEqual([ amol ], ww.employees)
        self.assertEqual(1, Association.count)


        # test reassignment
        ww.employees = [ dp ]
        self.assertEqual([ dp ], ww.employees)
        self.assertEqual(1, Association.count)

        ww.employees = []
        self.assertEqual([], ww.employees)
        self.assertEqual(0, Association.count)


    def test_delete_op(self):
        ww.employees = [ amol ]
        self.assertEqual([ amol ], ww.employees)
        self.assertEqual(1, Association.count)

        # deleting attribute simply forces reload
        del ww.employees
        self.assertEqual([ amol ], ww.employees)

        # deleting list item should work as expected
        del ww.employees[0]
        self.assertEqual([], ww.employees)
        self.assertEqual(0, Association.count)


    def test_single(self):
        self.assertEqual(None, ww.ceo)
        self.assertEqual(0, Association.count)

        ww.ceo = jarah
        self.assertEqual(jarah, ww.ceo)
        self.assertEqual(1, Association.count)

        ww.ceo = amol
        self.assertEqual(amol, Company.first.ceo)
        self.assertEqual(1, Association.count)

        ww.ceo = None
        self.assertEqual(0, Association.count)


    def test_cascade(self):
        self.assertIn('delete-orphan', Company.ceo.property.cascade)

        ww.ceo = jarah
        self.assertEqual(3, Employee.count)

        # assoc delete should cascade and also delete Employee
        ww.ceo = None
        self.assertEqual(2, Employee.count)


    def test_type(self):
        ww.employees << dp
        self.assertEqual('employees', Association.all[-1].assoc_type)

        ww.ceo = jarah
        self.assertEqual('ceo', Association.all[-1].assoc_type)

        ww.mvp = amol
        self.assertEqual('favorite', Association.all[-1].assoc_type)


    def test_property(self):
        self.assertEqual(MANYTOMANY, Company.employees.property.direction)
        self.assertTrue(Company.employees.property.uselist)

        self.assertEqual(MANYTOMANY, Company.ceo.property.direction)
        self.assertFalse(Company.ceo.property.uselist)



if __name__ == '__main__':
    unittest.main()
