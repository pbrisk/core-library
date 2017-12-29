# coding=utf-8

from corelibrary.base.baseobject import AnalyticsObject
from corelibrary.base.interface.riskfactor import RiskFactorInterface


class FactorModel(AnalyticsObject):
    """ FactorModel base class """

    def pre_calculate(self):
        """
            pre calculation depending only on model data
        """
        pass

    def get_state(self, state):
        """ calculates the next state

        :param RiskFactorState state: last producer state state
        :return: RiskFactorState
        """
        return state


class RiskFactor(RiskFactorInterface):
    """ RiskFactor base class """

    def __init__(self, object_name_str=''):
        super(RiskFactor, self).__init__(object_name_str)
        self._initial_factor_value_ = 0.0
        self._risk_factor_state = self._initial_factor_value_
        self._risk_factor_date = self.origin

    def _rebuild_object(self):
        super(RiskFactor, self)._rebuild_object()
        self.set_risk_factor(self.origin, self._initial_factor_value_)

    def set_risk_factor(self, factor_date, factor_value):
        """ set risk factor driver value of  risk factor

        :param factor_date:
        :param factor_value:
        :return:
        """
        self._risk_factor_state = factor_value
        self._risk_factor_date = factor_date