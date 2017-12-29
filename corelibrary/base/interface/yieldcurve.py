# coding=utf-8

from businessdate import BusinessPeriod
from dcf import simple_rate, continuous_rate

from corelibrary.base.baseobject import AnalyticsObject


class YieldCurveInterface(AnalyticsObject):
    """ interface class for YieldCurve type objects """

    @property
    def curve(self):
        """ inner curve """
        return NotImplemented

    @property
    def domain(self):
        """ list of grid date of curve """
        return NotImplemented

    def _day_count(self, start_date, end_date):
        """
        calculates day count

        :param BusinessDate end_date:
        :param BusinessDate start_date:
        :return float:
        """
        return NotImplemented

    def get_discount_factor(self, start_date, end_date):
        """
        calculates discount factor

        :param BusinessDate start_date: date to discount to
        :param BusinessDate end_date: date to discount from
        :return float: discount factor
        """
        raise NotImplementedError

    def get_zero_rate(self, start_date, end_date):
        """
        calculates zero rate

        :param BusinessDate end_date:
        :param BusinessDate start_date:
        :return float:
        """
        df = self.get_discount_factor(start_date, end_date)
        t = self._day_count(start_date, end_date)
        return continuous_rate(df, t)

    def get_cash_rate(self, start_date, end_date=None, tenor_period=BusinessPeriod('1y')):
        """

        :param start_date:
        :param end_date:
        :param tenor_period:
        :return:
        """
        end_date = start_date + tenor_period if end_date is None else end_date
        df = self.get_discount_factor(start_date, end_date)
        t = self._day_count(start_date, end_date)
        return simple_rate(df, t)
