# coding=utf-8

from corelibrary.base.baseobject import AnalyticsObject


class VolInterface(AnalyticsObject):
    """ interface class for Volatility type objects """

    def get_volatility(self, strike_value, start_date, end_date):
        """

        :param date:
        :param strike:
        :return:
        """
        raise NotImplementedError

    def get_variance(self, strike_value, start_date, end_date):
        """

        :param strike_value:
        :param start_date:
        :param end_date:
        :return:
        """
        raise NotImplementedError


class ImpliedVolInterface(VolInterface):
    """ interface class for Volatility type objects """

    @property
    def option_pricer(self):
        """ option pricer """
        raise NotImplementedError
