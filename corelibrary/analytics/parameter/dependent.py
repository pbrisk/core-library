# coding=utf-8

from corelibrary.base.baseobject import AnalyticsObject
from corelibrary.base.interface.fxcurve import FxCurveInterface
from corelibrary.base.interface.yieldcurve import YieldCurveInterface

from dcf.curve import DateCurve
from math import exp, log


class DependentFactor(AnalyticsObject):
    """ base class to build scenarios of factors """

    def __init__(self, object_name_str=''):
        super(DependentFactor, self).__init__(object_name_str)
        self._inner_factor_ = AnalyticsObject()
        self._driving_factor_ = AnalyticsObject()

        self._spread = None


class DependentDefaultProbability(DependentFactor):
    """ scenarios for DefaultProbability """
    pass


class DependentFxCurve(DependentFactor):
    """ scenarios for _fx_curve_ """

    def __init__(self, object_name_str=''):
        super(DependentFxCurve, self).__init__(object_name_str)
        self._inner_factor_ = FxCurveInterface()
        self._driving_factor_ = FxCurveInterface()

    def _rebuild_object(self):
        super(DependentFxCurve, self)._rebuild_object()
        self._spread = self._inner_factor_.get_value(self.origin)
        self._spread /= self._driving_factor_.get_value(self.origin)

    def get_value(self, reset_date, base_date=None, index_model_dict={}):
        """
        :param reset_date:
        :param base_date:
        :return float:
        """
        return self._spread * self._driving_factor_.get_value(self.origin)


class DependentYieldCurve(DependentFactor, YieldCurveInterface):
    """ Yieldcurves that depend on a driving force"""

    @property
    def domain(self):
        return self._domain

    def _day_count(self, start_date, end_date):
        return self._inner_factor_._day_count(start_date, end_date)

    def __init__(self, object_name_str=''):
        super(DependentYieldCurve, self).__init__(object_name_str)
        self._inner_factor_ = YieldCurveInterface()
        self._driving_factor_ = YieldCurveInterface()
        self._domain = list()
        self._spread = DateCurve([20151231,20660101],[0, 0])

    def _rebuild_object(self):
        super(DependentYieldCurve, self)._rebuild_object()
        self._domain = sorted(list(set(self._inner_factor_.domain).union(set(self._driving_factor_.domain))))
        self._origin_ = self._driving_factor_.origin

        spread_values_on_domain = [self._inner_factor_.get_zero_rate(self._inner_factor_.origin, d)
                                   - self._driving_factor_.get_zero_rate(self._driving_factor_.origin, d)
                                   for d in self.domain]

        self._spread = DateCurve(self.domain, spread_values_on_domain, day_count=self._day_count)

    def get_zero_rate(self, start_date, end_date):
        """
        calculates zero rate

        :param BusinessDate end_date:
        :param BusinessDate start_date:
        :return float:
        """
        start_date, end_date = self._inner_factor_._cast_to_dates(start_date, end_date)


        origin = self._inner_factor_.origin
        daycount = self._day_count(start_date, end_date)
        'tZ = daycount(0,t)*(driving_Zerorate(t)+Zero_spread(t))'
        eZ = self._day_count(origin, end_date)*\
             (self._driving_factor_.get_zero_rate(origin, end_date)+self._spread(end_date))
        if start_date != origin:
            sZ = self._day_count(origin, start_date)*\
                (self._driving_factor_.get_zero_rate(origin, start_date)+ self._spread(start_date))
        else:
            sZ = 0

        return 1/daycount*(eZ-sZ) if daycount != 0 else 0

    def get_discount_factor(self, start_date, end_date):
        """
        calculates discount factor

        :param BusinessDate start_date: date to discount to
        :param BusinessDate end_date: date to discount from
        :return float: discount factor
        """
        start_date, end_date = self._inner_factor_._cast_to_dates(start_date, end_date)
        return exp(-1*self._day_count(start_date, end_date)*self.get_zero_rate(start_date, end_date))


class DependentVol(DependentFactor):
    """ scenarios for Vol """
    pass
