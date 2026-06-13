#!/usr/bin/env python

import unittest

from sqlalchemy import *
from sqlalchemy.orm.interfaces import MANYTOMANY

from tests.support import BaseModel, TestBase
from sqlalchemy_lightening.association import association, init_assocs, Association


init_assocs(BaseModel)

class Company(BaseModel):
    name = Column(String)
    employees = association('Employee')
    ceo = association('Employee', uselist=False, single_parent=True, cascade='all, delete-orphan')
    mvp = association('Employee', type='favorite', uselist=False)


class Employee(BaseModel):
    name = Column(String)
    laptop = association('Laptop', uselist=False, cascade='all, delete-orphan')


class Laptop(BaseModel):
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

        # expiring the attribute forces a reload from the association table
        self.session.expire(ww, [ 'employees' ])
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
        self.assertIn('delete-orphan', Company.ceo.property.assoc_cascade)

        ww.ceo = jarah
        self.assertEqual(3, Employee.count)

        # assoc delete should cascade and also delete Employee
        ww.ceo = None
        self.assertEqual(2, Employee.count)


    def test_delete_cleans_up_associations(self):
        # deleting the parent removes its association rows
        ww.employees << dp
        ww.employees << amol
        self.assertEqual(2, Association.count)

        ww.delete()
        self.session.flush()

        self.assertEqual(0, Association.count)
        # a plain association leaves the targets intact
        self.assertEqual(3, Employee.count)


    def test_delete_cascades_to_targets(self):
        # with a delete cascade, deleting the parent also deletes the targets
        ww.ceo = jarah
        self.session.flush()
        self.assertEqual(1, Association.count)
        self.assertEqual(3, Employee.count)

        ww.delete()
        self.session.flush()

        self.assertEqual(0, Association.count)
        self.assertEqual(2, Employee.count)

        # the cascaded target is removed from the session, not left stale
        self.assertTrue(inspect(jarah).deleted)
        self.assertNotIn(jarah, self.session)


    def test_delete_cascade_recurses(self):
        # cascade follows the chain: Company -> Employee -> Laptop
        ww.ceo = jarah
        jarah.laptop = Laptop(name='mbp').save()
        self.session.flush()
        self.assertEqual(2, Association.count)
        self.assertEqual(1, Laptop.count)

        ww.delete()
        self.session.flush()

        self.assertEqual(0, Association.count)
        self.assertEqual(2, Employee.count)
        self.assertEqual(0, Laptop.count)


    def test_associate_before_target_has_id(self):
        # a saved-but-unflushed target can be associated; its id resolves
        mbp = Laptop(name='mbp').save()
        self.assertIsNone(mbp.id)

        jarah.laptop = mbp
        self.session.flush()

        self.assertEqual(mbp.id, Association.all[-1].to_id)
        self.assertEqual(mbp, jarah.laptop)


    def test_associate_persists_unsaved_object(self):
        # associating an unsaved object persists it (save-update cascade)
        ghost = Employee(name='ghost')
        ww.employees << ghost
        self.session.flush()

        self.assertIsNotNone(ghost.id)
        self.assertIn(ghost, ww.employees)
        self.assertEqual(4, Employee.count)


    def test_associate_without_session_raises(self):
        # with no session to persist into, ids can't be resolved
        startup = Company(name='startup')
        with self.assertRaises(ValueError):
            startup.employees << Employee(name='founder')


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
