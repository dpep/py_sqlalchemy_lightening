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
grass = Food(name='grass').save()
brownie.food = grass



class BasicTest(unittest.TestCase):
    def test_upgrade(self):
        # was implicitly upgraded to Rekeyable and Pluckable
        self.assertTrue(hasattr(dp.pets, 'rekey'))
        self.assertTrue(hasattr(dp.pets, 'pluck'))


    def test_shift_upgrade(self):
        # lshift is aliased to append
        pet = Pet(name='sammy')
        dp.pets << pet

        self.assertIn(pet, dp.pets)


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
        self.assertEqual(
            grass,
            brownie.food
        )

        # test update
        brownie.food = carrots

        # implicitly updated by event handler
        self.assertEqual(
            carrots.id,
            brownie.food_id
        )

        self.assertEqual(
            carrots,
            brownie.food
        )

        # test delete
        brownie.food = None
        self.assertIsNone(brownie.food_id)




if __name__ == '__main__':
    unittest.main()
