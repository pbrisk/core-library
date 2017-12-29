# coding=utf-8
from corelibrary.base.baseobject import AnalyticsObject


# general class to store arbitrary properties
class Result(AnalyticsObject):
    """ Result object """

    def __getattr__(self, item):
        try:
            vp = self.__class__._to_visible(item)
            return super(Result, self).__getattribute__(vp)
        except AttributeError:
            return super(Result, self).__getattribute__(item)

    def _modify_property(self, property_name, property_value_variant):
        vp = self.__class__._to_visible(property_name)
        try:
            setattr(self, vp, property_value_variant)
        except AttributeError:
            s = str(property_value_variant), str(vp)
            raise AttributeError("can't set value %s to attribute %s" % s)
        return super(Result, self)._modify_property(property_name, property_value_variant)
