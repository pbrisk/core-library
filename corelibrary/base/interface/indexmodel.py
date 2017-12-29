# coding=utf-8

from businessdate import BusinessDate

from corelibrary.base.baseobject import AnalyticsObject


class IndexModelInterface(AnalyticsObject):
    """ interface class for index model objects """

    def get_value(self, index_object, reset_date, base_date=None):
        """

        :param Index index_object:
        :param BusinessDate reset_date:
        :param BusinessDate base_date:
        :return float:
        """
        raise NotImplementedError


class StochasticIndexModelInterface(IndexModelInterface):
    """ interface class for index model objects """

    def get_option_payoff_value(self, index_object, option_payoff_name, strike_value, reset_date, base_date=None):
        """

        :param Index index_object:
        :param OptionPayoffType option_payoff_name:
        :param float strike_value:
        :param BusinessDate reset_date:
        :param BusinessDate base_date:
        :return: float
        """
        raise NotImplementedError


class SwapRateIndexModelInterface(IndexModelInterface):
    """ index interface for swap rates """

    def get_annuity_value(self, index_object, value_date, base_date=BusinessDate(), cash=False):
        """ calculate get_annuity_value for either cash or physical settlement

        :param SwapRateIndexInterface index_object:
        :param BusinessDate value_date:
        :param BusinessDate base_date: (optional) default is BusinessDate()
        :param boolean cash: if True, get_annuity_value for cash settlement else for physical settlement
                             (optional) default is False
        :return: float
        """
        raise NotImplementedError
