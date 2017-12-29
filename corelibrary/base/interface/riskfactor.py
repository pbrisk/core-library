# coding=utf-8

from corelibrary.base.baseobject import AnalyticsObject


class RiskFactorInterface(AnalyticsObject):
    """ interface class for risk factor objects """

    def set_risk_factor(self, factor_date, factor_value):
        """ set risk factor driver value of  risk factor

        :param factor_date:
        :param factor_value:
        :return:
        """
        raise NotImplementedError