# coding=utf-8
""" UnitTests for the functionality of the products """
from unittest import TestCase, main
import corelibrary


class InstanceUnitTests(TestCase):
    def test_business_objects(self):
        for a in dir(corelibrary):
            cls = getattr(corelibrary, a)
            if isinstance(cls, type) and issubclass(cls, corelibrary.BusinessObject):
                self.assertTrue(cls())

    def test_analytics_objects(self):
        for a in dir(corelibrary):
            cls = getattr(corelibrary, a)
            if isinstance(cls, type) and issubclass(cls, corelibrary.AnalyticsObject):
                if issubclass(cls, corelibrary.VisibleFloat):
                    self.assertTrue(cls(1.))
                else:
                    self.assertTrue(cls())

    def test_named_objects(self):
        for a in dir(corelibrary):
            cls = getattr(corelibrary, a)
            if isinstance(cls, type) and issubclass(cls, corelibrary.FactoryObject) and not issubclass(cls, corelibrary.VisibleObject):
                self.assertTrue(cls())
