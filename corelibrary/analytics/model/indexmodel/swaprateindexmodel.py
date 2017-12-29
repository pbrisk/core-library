# coding=utf-8
from businessdate import BusinessDate

from corelibrary.base.interface.indexmodel import SwapRateIndexModelInterface

from rateindexmodel import InterestRateIndexModel, OptionIndexModel


class SwapRateIndexModel(InterestRateIndexModel, SwapRateIndexModelInterface, OptionIndexModel):
    """ swap rate index base, defines methods for the a swap rate index. """

    @property
    def _discount_index(self):
        return NotImplemented

    def _swap_annuity(self, index_object, value_date, base_date):
        """ calculate get_annuity_value as sum of df

        :param value_date:
        :param base_date:
        :return:
        """
        fix_cash_flow_list, = index_object.get_underlying_swap(value_date).fix_list
        disc_index = self._discount_index
        ret = 0.0
        for cf in fix_cash_flow_list:
            df = index_object.discount_index.get_value(cf.pay_date, base_date)
            ret += abs(cf.notional) * cf.year_fraction * df
        return ret

    def _cash_annuity(self, index_object, value_date, base_date):
        """ calculate get_annuity_value for cash settlement

        :param index_object:
        :param value_date:
        :param base_date:
        :return:
        """
        fix_cash_flow_list, = index_object.get_underlying_swap(value_date).fix_list
        freq = round(sum([cf.year_fraction for cf in fix_cash_flow_list]) / float(len(fix_cash_flow_list)), 0)
        fwd_swap_rate = self.get_value(index_object, value_date, base_date)
        t = 0.0
        d = 1.0 + fwd_swap_rate / freq
        ret = 0.0
        for cf in fix_cash_flow_list:
            t += cf.year_fraction
            df = d ** (-t * freq)
            ret += abs(cf.notional) * cf.year_fraction * df
        df0 = index_object.discount_index.get_value(base_date=base_date, reset_date=value_date)
        return ret * df0

    def get_annuity_value(self, index_object, value_date, base_date=BusinessDate(), cash=False):
        """ calculate get_annuity_value for either cash or physical settlement

        :param BusinessDate value_date:
        :param BusinessDate base_date: (optional) default is BusinessDate()
        :param boolean cash: if True, get_annuity_value for cash settlement else for physical settlement
                             (optional) default is False
        :return: float
        """
        if cash:
            return self._cash_annuity(index_object, value_date, base_date)
        else:
            return self._swap_annuity(index_object, value_date, base_date)

    def get_value(self, index_object, reset_date, base_date=None):
        """
        returns the projected forward rate

        :param BusinessDate reset_date: fixing date
        :param BusinessDate base_date:
        :return: float

        the fair rate of the underlying swap.
        """
        fair_rate = index_object.get_underlying_swap(reset_date).get_fair_rate(reset_date)  # todo: feed index_model_dict?
        return fair_rate
