#!/usr/bin/env python

import unittest

from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property

from tests.support import BaseModel, TestBase


class Rectangle(BaseModel):
    length = Column(Integer)
    width = Column(Integer)

    @hybrid_property
    def size(self):
        return self.length * self.width


class HybridPropertyTest(TestBase):
    def test_properties(self):
        small = Rectangle(length=2, width=3).save()

        self.assertEqual(
            6,
            small.size
        )

        self.assertEqual(
            small,
            Rectangle.where(Rectangle.size == 6).one()
        )

        self.assertEqual(
            small,
            Rectangle.where(size=6).one()
        )



if __name__ == '__main__':
    unittest.main()
