# coding=utf-8
"""
interest rate vol module
"""

from math import exp

from businessdate import BusinessDate, BusinessPeriod
from putcall import OptionValuatorN, OptionValuatorLN, OptionValuatorSLN

from basevol import ImpliedVol
from corelibrary.base.baseobject import DataRange


class RateVol(ImpliedVol):
    """ RateVol """
    pass


class NormalBlackVol(RateVol):
    """ NormalBlackVol """

    def __init__(self, object_name_str=''):
        super(NormalBlackVol, self).__init__(object_name_str)
        self._option_pricer = OptionValuatorN()

    def get_variance(self, strike_value, start_date, end_date):
        """

        :param strike_value:
        :param start_date:
        :param end_date:
        :return:
        """
        time = self.day_count(start_date, end_date)
        vol = self._surface.get_value(time, strike_value)
        v2t = vol * vol * time
        return v2t, vol, time


class BlackVol(RateVol):
    """ log normal Black volatility """

    def __init__(self, object_name_str=''):
        super(BlackVol, self).__init__(object_name_str)
        self._option_pricer = OptionValuatorLN()

    def get_variance(self, strike_value, start_date, end_date):
        """

        :param strike_value:
        :param start_date:
        :param end_date:
        :return:
        """
        time = self.day_count(start_date, end_date)
        vol = self._surface.get_value(time, strike_value)
        v2t = vol * vol * time
        return strike_value * strike_value * (exp(v2t) - 1), vol


class ShiftedBlackVol(BlackVol):
    """ shifted log-normal Black vol """

    def __init__(self, object_name_str=''):
        super(ShiftedBlackVol, self).__init__(object_name_str)
        self._displacement_ = 0.03
        self._option_pricer = OptionValuatorSLN(self._displacement_)


# -----

class SwaptionVolN(NormalBlackVol):
    """ SwaptionVolN """
    def __init__(self, object_name_str=''):
        super(SwaptionVolN, self).__init__(object_name_str)
        self._swap_tenor_ = BusinessPeriod()


class CapletVolN(NormalBlackVol):
    """ CapletVolN """
    pass


class CapletVolLN(BlackVol):
    """ CapletVolLN """
    pass


class CapletVolSLN(ShiftedBlackVol):
    """ CapletVolSLN """
    pass


# -----

class SabrVol(RateVol):
    """ SabrVol """
    pass


class ShiftedSabrVol(RateVol):
    """ ShiftedSabrVol """
    pass


class ArbitrageFreeSabrVol(RateVol):
    """ ArbitrageFreeSabrVol """
    pass


class HWVol(RateVol):
    """ HWVol """

    def __init__(self, object_name_str=''):
        super(HWVol, self).__init__(object_name_str)
        self._curve_ = DataRange([['', 'Value'], [BusinessDate(), 0.1]])
        self._vol_ = DataRange([['', 'Value'], [BusinessDate(), 0.1]])
        self._mean_reversion_ = DataRange([['', 'Value'], [BusinessDate(), 0.1]])
