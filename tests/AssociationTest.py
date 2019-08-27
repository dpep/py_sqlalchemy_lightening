#!/usr/bin/env python

import os
import sys
import unittest

from sqlalchemy import *

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '.')) ] + sys.path

from support import BaseModel, TestBase
# from sqlalchemy_lightening import relationship

# import sqlalchemy_lightening.association
from sqlalchemy_lightening.association import association, init_assocs, Association


init_assocs(BaseModel)

class Company(BaseModel):
    name = Column(String, nullable=False)
    employees = association('employees', 'Employee')


class Employee(BaseModel):
    name = Column(String, nullable=False)

#     department_id = Column(Integer, index=True)
#     department = relationship('Department')


# class Department(BaseModel):
#     name = Column(String, nullable=False)



class AssociationTest(TestBase):
    def seed(self):
        global ww, dp, amol, eng
        ww = Company(name='WorkWhile').save()
        dp = Employee(name='dpepper').save()
        amol = Employee(name='amol').save()
        # eng = Department(name='engineering').save()


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


# TODO: test delete cascades


if __name__ == '__main__':
    unittest.main()
