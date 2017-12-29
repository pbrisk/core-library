# coding=utf-8
"""
base vol module
"""

from math import exp

from businessdate import BusinessDate, BusinessPeriod
from putcall import OptionType, OptionValuatorLN, OptionValuatorIntrinsic

from corelibrary.base.baseobject import DataTable
from corelibrary.base.interface.vol import VolInterface
from corelibrary.base.namedobject import ModFollow, TAR, Act360

from corelibrary.utils.maths import Surface


class Vol(VolInterface):
    """ Vol class """

    @property
    def day_count(self):
        """ day_count calculation function """
        return self._day_count_.get_year_fraction

    def __init__(self, object_name_str=''):
        super(Vol, self).__init__(object_name_str)
        self._calendar_ = TAR()
        self._spot_ = BusinessPeriod(businessdays=2, holiday=self._calendar_)
        self._rolling_method_ = ModFollow()
        self._day_count_ = Act360()
        self._surface_ = DataTable()
        self._surface = Surface([0.], [0.], [[0.]])
        self._option_pricer = OptionValuatorLN()

    def _rebuild_object(self):
        def try_get_business_period(val):
            if isinstance(val, BusinessPeriod):
                return val
            if isinstance(val, str):
                y, m, d = BusinessPeriod.parse(val)
                if y > 0 or m > 0 or d > 0:
                    return BusinessPeriod(years=y, months=m, days=d)
                else:
                    return None

        super(Vol, self)._rebuild_object()
        if self._surface_:
            strike_list = self._surface_.col_keys()
            expiry_list = list()
            for e in self._surface_.row_keys():
                p = try_get_business_period(e)
                if not p is None:
                #if isinstance(e, BusinessPeriod):
                    # fixme e = self.ObjectOrigin.add_period(self.Spot, self.Calendar).add_period(p, self.Calendar)
                    s = self.origin.add_period(self._spot_, self._calendar_)
                    e = s.add_period(p).add_business_days(-self._spot_.businessdays, self._calendar_)
                if isinstance(e, BusinessDate):
                    e = self._day_count_.get_year_fraction(self.origin, e)
                expiry_list.append(e)
            self._surface = Surface(expiry_list, strike_list, self._surface_)
        return self

    def get_volatility(self, strike_value, start_date, end_date):
        """

        :param strike_value:
        :param start_date:
        :param end_date:
        :return:
        """
        time = self.day_count(start_date, end_date)
        vol = self._surface.get_value(time, strike_value)
        return vol


class ImpliedVol(Vol):
    """ ImpliedVol class """

    @property
    def option_pricer(self):
        """ option pricer """
        return self._option_pricer


class IntrinsicModelVol(ImpliedVol):
    """ IntrinsicModelVol """

    def __init__(self, object_name_str=''):
        super(IntrinsicModelVol, self).__init__(object_name_str)
        self._surface = Surface([0.], [0.], [[0.]])
        self._option_pricer = OptionValuatorIntrinsic()

    def _rebuild_object(self):
        super(IntrinsicModelVol, self)._rebuild_object()
        self._surface = Surface([0.], [0.], [[0.]])
        self._option_pricer = OptionValuatorIntrinsic()
