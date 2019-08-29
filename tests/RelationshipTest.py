#!/usr/bin/env python

import os
import sys
import unittest

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOONE

sys.path = [ os.path.abspath(os.path.dirname(__file__)) ] + sys.path

from support import BaseModel, TestBase
from sqlalchemy_lightening import relationship


class Human(BaseModel):
    name = Column(String, nullable=False)
    pets = relationship('Pet')


class Pet(BaseModel):
    name = Column(String, nullable=False)
    human_id = Column(Integer, index=True)

    food_id = Column(Integer)
    food = relationship('Food')

    treat_id = Column(Integer)
    treat = relationship('Food')


class Food(BaseModel):
    name = Column(String, unique=True)



class BasicTest(TestBase):
    def seed(self):
        global dp, brownie, jp, carrots, grass, apple

        dp = Human(name='dpepper').save()
        brownie = Pet(name='brownie').save()
        dp.pets.append(brownie)

        jp = Human(name='josh').save()

        carrots = Food(name='carrots').save()
        grass = Food(name='grass').save()
        apple = Food(name='apple').save()


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
            ONETOMANY,
            Human.pets.property.direction
        )
        self.assertTrue(Human.pets.property.uselist)

        self.assertEqual(
            [ dp.id ],
            dp.pets.pluck('human_id')
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
            MANYTOONE,
            Pet.food.property.direction
        )
        self.assertFalse(Pet.food.property.uselist)

        brownie.food = grass

        self.assertEqual(
            grass,
            brownie.food
        )

        # foreign key implicitly updated by event handler
        self.assertEqual(
            grass.id,
            brownie.food_id
        )

        # test update
        brownie.food = carrots

        self.assertEqual(
            carrots,
            brownie.food
        )

        self.assertEqual(
            carrots.id,
            brownie.food_id
        )

        # test delete
        brownie.food = None
        self.assertIsNone(brownie.food)
        self.assertIsNone(brownie.food_id)


    def test_many_to_one_foreign_key(self):
        '''
        Ensure that setting the foreign key column correctly resets
        the relationship value, ie. changing Pet.food_id changes Pet.food
        '''
        hopper = Pet(name='hopper').save()
        carrots = Food.where(name='carrots').one()
        grass = Food.where(name='grass').one()
        Pet.query.session.flush()

        self.assertIsNone(hopper.food)
        self.assertIsNone(hopper.food_id)

        hopper.food_id = carrots.id

        self.assertEqual(
            carrots.id,
            hopper.food_id
        )

        # implicitly updated by event handler
        self.assertEqual(
            carrots,
            hopper.food
        )

        hopper.food_id = grass.id

        self.assertEqual(
            grass.id,
            hopper.food_id
        )

        self.assertEqual(
            grass,
            hopper.food
        )

        hopper.food_id = None
        self.assertIsNone(hopper.food_id)
        self.assertIsNone(hopper.food)


    def test_secondary_many_to_one(self):
        '''
        key name may differ from foreign table name,
          eg. Pet.treat_id maps to Food.id
        '''
        self.assertIsNone(brownie.treat_id)
        self.assertIsNone(brownie.treat)
        self.assertIsNone(brownie.food)

        brownie.treat = apple

        self.assertEqual(
            apple,
            brownie.treat
        )
        self.assertEqual(
            apple.id,
            brownie.treat_id
        )

        # should not have changed
        self.assertIsNone(brownie.food)

        brownie.food = grass
        self.assertEqual(
            grass.id,
            brownie.food_id
        )

        # should not have changed
        self.assertEqual(
            apple.id,
            brownie.treat_id
        )

        # test delete
        brownie.treat = None
        self.assertIsNone(brownie.treat)
        self.assertIsNone(brownie.treat_id)

        # should not have changed
        self.assertEqual(
            grass.id,
            brownie.food_id
        )


if __name__ == '__main__':
    unittest.main()
