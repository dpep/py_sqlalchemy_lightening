#!/usr/bin/env python

import os
import sys
import unittest

sys.path = [ os.path.abspath(os.path.join(os.path.dirname(__file__), '.')) ] + sys.path

from models import Person, Pet, Food


Person.query.delete()
Pet.query.delete()
Food.query.delete()

dp = Person(name='dpepper').save()
brownie = Pet(name='brownie')
dp.pets.append(brownie)

jp = Person(name='josh').save()

carrots = Food(name='carrots').save()
brownie.food = carrots



class BasicTest(unittest.TestCase):
    def test_upgrade(self):
        # was implicitly upgraded to Rekeyable and Pluckable
        self.assertTrue(hasattr(dp.pets, 'rekey'))
        self.assertTrue(hasattr(dp.pets, 'pluck'))


    def test_one_to_many(self):
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


    def test_many_to_one(self):
        # TODO: fix with better test isolation with seeding
        # self.assertEqual(
        #     carrots.id,
        #     brownie.food_id
        # )

        self.assertEqual(
            carrots,
            brownie.food
        )




if __name__ == '__main__':
    unittest.main()
