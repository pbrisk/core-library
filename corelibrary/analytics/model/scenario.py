# coding=utf-8

from corelibrary.base.baseobject import AnalyticsObject
from corelibrary.base.interface.yieldcurve import YieldCurveInterface
from corelibrary.base.interface.fxcurve import FxCurveInterface


class ScenarioFactor(AnalyticsObject):
    """ base class to build scenarios of factors """

    def __init__(self, object_name_str=''):
        super(ScenarioFactor, self).__init__(object_name_str)
        self._inner_factor_ = AnalyticsObject()
        self._driving_factor_ = AnalyticsObject()

        self._spread = None


class ScenarioDefaultProbability(ScenarioFactor):
    """ scenarios for DefaultProbability """
    pass


class ScenarioFxCurve(ScenarioFactor, FxCurveInterface):
    """ scenarios for _fx_curve_ """

    def __init__(self, object_name_str=''):
        super(ScenarioFxCurve, self).__init__(object_name_str)
        self._inner_factor_ = FxCurveInterface()
        self._driving_factor_ = FxCurveInterface()

    def _rebuild_object(self):
        super(ScenarioFxCurve, self)._rebuild_object()
        self._spread = self._inner_factor_.get_value(self.origin)
        self._spread /= self._driving_factor_.get_value(self.origin)

    def get_value(self, reset_date):
        """
        :param reset_date:
        :param base_date:
        :return float:
        """
        return self._spread * self._driving_factor_.get_value(self.origin)


class ScenarioYieldCurve(ScenarioFactor, YieldCurveInterface):
    """ scenarios for YieldCurveInterface """

    def __init__(self, object_name_str=''):
        super(ScenarioYieldCurve, self).__init__(object_name_str)
        self._inner_factor_ = YieldCurveInterface()
        self._driving_factor_ = YieldCurveInterface()

    def _rebuild_object(self):
        super(ScenarioYieldCurve, self)._rebuild_object()
        self._spread = self._inner_factor_.curve
        self._spread -= self._driving_factor_.curve.curve

    def get_zero_rate(self, start_date, end_date):
        """
        calculates zero rate

        :param BusinessDate end_date:
        :param BusinessDate start_date:
        :return float:
        """
        start_date, end_date = self._cast_to_dates(start_date, end_date)

        zero_rate = self._driving_factor_.get_zero_rate(start_date, end_date)
        zero_rate += self._spread.get_zero_rate(start_date, end_date)
        return zero_rate

    def get_discount_factor(self, start_date, end_date):
        """
        calculates discount factor

        :param BusinessDate start_date: date to discount to
        :param BusinessDate end_date: date to discount from
        :return float: discount factor
        """
        start_date, end_date = self._cast_to_dates(start_date, end_date)

        discount_factor = self._driving_factor_.get_discount_factor(start_date, end_date)
        discount_factor *= self._spread.get_discount_factor(start_date, end_date)
        return discount_factor


class ScenarioVol(ScenarioFactor):
    """ scenarios for Vol """
    pass
