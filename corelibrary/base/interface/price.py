# coding=utf-8

from corelibrary.base.baseobject import AnalyticsObject, VisibleFloat


class PriceInterface(AnalyticsObject, VisibleFloat):
    """ VisibleObject interface which is also a float. Useful to have Price or SpotFxRates to be AnalyticsObjects. """
    pass
