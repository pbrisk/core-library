# coding=utf-8
"""
defining fair rate interface
"""

from businessdate import BusinessDate

from corelibrary.base.baseobject import AnalyticsObject


class FairRateInterface(AnalyticsObject):
    """ interface for having a fair rate (par rate) """

    def get_fair_rate(self, value_date=BusinessDate(), index_model_dict={}):
        """ calculate fair rate of an InterestRateSwap

        :param value_date:
        :param index_model_dict:
        :return: float: the fair rate of the underlying swap.
        :rtype: fair_rate
        """
        raise NotImplementedError
