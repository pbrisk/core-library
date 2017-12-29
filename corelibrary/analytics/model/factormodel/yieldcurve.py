# coding=utf-8

from shortrate import HullWhiteCurve as _HullWhiteCurve

from corelibrary.base.interface.yieldcurve import YieldCurveInterface

from basefactormodel import RiskFactor


class HullWhiteCurve(RiskFactor, YieldCurveInterface):
    """ HullWhiteCurve """

    @property
    def curve(self):
        """ inner curve """
        return self._curve_

    @property
    def domain(self):
        """ list of grid date of curve """
        return list(self.curve.domain)

    def __init__(self, object_name_str=''):
        super(HullWhiteCurve, self).__init__(object_name_str)
        self._curve_ = YieldCurveInterface()
        self._mean_reversion_ = 0.01
        self._volatility_ = 0.02
        self._hull_white_curve = _HullWhiteCurve([0.0], [0.0])

    def _rebuild_object(self):
        super(HullWhiteCurve, self)._rebuild_object()
        hw = _HullWhiteCurve.cast(self._curve_.curve, self._mean_reversion_, self._volatility_)
        self._hull_white_curve = hw

    def _day_count(self, start_date, end_date):
        return self._curve_._day_count(start_date, end_date)

    def set_risk_factor(self, factor_date, factor_value):
        """ set risk factor

        :param factor_date:
        :param factor_value:
        """
        self._risk_factor_state = factor_value
        self._risk_factor_date = factor_date
        self._hull_white_curve.set_risk_factor(factor_date, factor_value)

    def get_discount_factor(self, start_date, end_date):
        """ get discount factor

        :param start_date:
        :param end_date:
        :return:
        """
        return self._hull_white_curve.get_discount_factor(start_date, end_date)