# coding=utf-8

from corelibrary.base.baseobject import AnalyticsObject


class FxCurveInterface(AnalyticsObject):
    """ interface class for YieldCurve type objects """

    def get_value(self, reset_date):
        """
        :param reset_date:
        :param base_date:
        :return float:
        """
        raise NotImplementedError