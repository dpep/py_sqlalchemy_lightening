#!/usr/bin/env python

import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '.')) ] + sys.path

from models import Person, Pet


Person.query.delete()
Pet.query.delete()

dp = Person(name='dpepper').save()
dp.pets.append(Pet(name='brownie'))

jp = Person(name='josh').save()


class BasicTest(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            [ dp.id ],
            dp.pets.pluck('person_id')
        )

        self.assertEqual(
            [ 'brownie' ],
            dp.pets.pluck('name')
        )

        self.assertEqual(
            [],
            jp.pets
        )


    def test_upgrade(self):
        # was implicitly upgraded to Rekeyable and Pluckable
        self.assertTrue(hasattr(dp.pets, 'rekey'))
        self.assertTrue(hasattr(dp.pets, 'pluck'))




if __name__ == '__main__':
    unittest.main()
