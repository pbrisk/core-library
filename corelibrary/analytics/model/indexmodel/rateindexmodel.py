# coding=utf-8
"""
interest rate index model
"""

import businessdate
from putcall import OptionValuatorN

from corelibrary.base.interface.index import RateIndexInterface, SwapRateIndexInterface
from corelibrary.base.interface.yieldcurve import YieldCurveInterface

from baseindexmodel import RiskNeutralIndexModel, OptionIndexModel


class InterestRateIndexModel(RiskNeutralIndexModel):
    """ base rate index """

    @property
    def yieldcurve(self):
        """ depending YieldCurve """
        return self._curve_

    def __init__(self, object_name_str=''):
        super(InterestRateIndexModel, self).__init__(object_name_str)
        self._curve_ = YieldCurveInterface()
        self._option_pricer = OptionValuatorN()


class DiscountIndexModel(InterestRateIndexModel):
    """ DiscountIndex """

    def get_value(self, index_object, reset_date, base_date=None):
        """

        :param index_object:
        :param reset_date:
        :param base_date:
        :return:
        """
        return self._curve_.get_discount_factor(base_date, reset_date)


class ZeroBondIndexModel(DiscountIndexModel):
    """ ZeroBondIndex """
    pass


class CashRateIndexModel(InterestRateIndexModel, OptionIndexModel):
    """ cash rate (LIBOR) index """

    def get_value(self, index_object, reset_date, base_date=None):
        """
        returns the projected forward rate

        :param Index index_object:
        :param BusinessDate reset_date: fixing date
        :param BusinessDate base_date:
        :return:

        float projected forward rate calculated over the _curve_
        """
        # a forward rate for a BusinessPeriod starting before the starting date of the _curve_ cannot be calculated
        start_date = index_object._rate_start_date(reset_date)
        end_date = index_object._rate_end_date(reset_date)
        return self._curve_.get_cash_rate(start_date, end_date)


class OverNightRateIndexModel(InterestRateIndexModel):
    """ over night index rate index """
    pass  # todo: really no changes for OverNightRateIndexModel


class ConvexityInterestRateIndexModel(InterestRateIndexModel, OptionIndexModel):
    """ ConvexityInterestRateIndexModel """

    def __init__(self, object_name_str=''):
        super(ConvexityInterestRateIndexModel, self).__init__(object_name_str)
        self._convexity_period_ = businessdate.BusinessPeriod("5B")
        self._discount_index_ = RateIndexInterface()  # fixme read from Index ???

    def get_value(self, index_object, reset_date, base_date=None):
        """

        :param Index() index_object:
        :param BusinessDate() reset_date:
        :param BusinessDate() base_date:
        :return float:
        """
        pay_currency = index_object.currency
        pay_date = reset_date
        index_forward = index_object.get_value(reset_date, base_date)
        if index_object.currency == pay_currency:
            if not self._is_almost_equal(pay_date, reset_date):
                adj, adj_vol = self._get_convexity_adjustment(index_object, index_forward, reset_date, pay_date)
                index_forward += adj
        else:
            raise Exception("Quanto adjustment not implemented yet.")
        return index_forward

    def _is_almost_equal(self, date1, date2):
        if date1 > date2:
            date1, date2 = date2, date1
        return businessdate.BusinessDate.diff_in_days(date1.add_period(self._convexity_period_), date2) < 1

    def _get_convexity_adjustment(self, index_object, unadjusted_index_value, reset_date, pay_date):
        end_date = index_object._rate_end_date(reset_date)
        variance, vol, time = self.vol.get_variance(unadjusted_index_value, self._vol_.origin, reset_date)
        if isinstance(index_object, SwapRateIndexInterface):
            alpha, beta = self._linear_rate_ansatz_swap(unadjusted_index_value, end_date, pay_date)
        else:
            alpha, beta = self._linear_rate_ansatz_cash(unadjusted_index_value, end_date, pay_date)
        f = unadjusted_index_value
        convex_adjust = beta / (alpha + beta * f) * variance
        return convex_adjust, vol

    def _linear_rate_ansatz_cash(self, unadjusted_index_value, end_date, pay_date):
        df = self._discount_index_.yieldcurve.get_discount_factor(end_date, pay_date)
        return 1.0, (df - 1.0) / unadjusted_index_value

    def _linear_rate_ansatz_swap(self, unadjusted_index_value, end_date, pay_date):
        raise Exception("linear_rate_ansatz_swap not implemented, yet")
