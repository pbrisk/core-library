# coding=utf-8

from businessdate import BusinessDate
from mitschreiben import Record

from corelibrary.base.baseobject import DataRange
from corelibrary.base.interface.fairerate import FairRateInterface
from corelibrary.business.index import CashRateIndex, OverNightRateIndex

from basederivative import SwapProduct
from cashflow import FixCashFlow, CashFlowList, CashFlowLegList


class InterestRateSwap(SwapProduct, FairRateInterface):
    """ InterestRateSwap base class """

    @property
    def start_date(self):
        """ min of all cashflow start dates"""
        return min(l.start_date for l in self.leg_list)

    @property
    def end_date(self):
        """ max of all cashflow end dates"""
        return max(l.end_date for l in self.leg_list)

    @property
    def pay_list(self):
        """ tuple of pay leg cashflows """
        return tuple(l for l in self.leg_list if l.is_pay)

    @property
    def rec_list(self):
        """ tuple of rec leg cashflows """
        return tuple(l for l in self.leg_list if l.is_rec)

    @property
    def fix_list(self):
        """ tuple of fix leg cashflows """
        return tuple(l for l in self.leg_list if l.is_fix)

    @property
    def float_list(self):
        """ tuple of float leg cashflows """
        return tuple(l for l in self.leg_list if l.is_float)

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns present value at value_date derived by given index_models if provided

        :param value_date:
        :param index_model_dict:
        :return: float, the pv of the cash flow
        """
        flow_list = list()
        for leg in self.leg_list:
            flow_list.extend(leg)
        return self._get_present_value_sum(flow_list, value_date, index_model_dict)

    @Record.Prefix()
    def get_fair_rate(self, value_date=BusinessDate(), index_model_dict={}):
        """ calculate fair rate of an InterestRateSwap

        :param value_date:
        :param index_model_dict:
        :return: float: the fair rate of the underlying swap.
        :rtype: fair_rate
        """
        float_list, = self.float_list
        pv_float_leg = sum(cf.get_present_value(value_date, index_model_dict) for cf in float_list)

        fix_list, = self.fix_list
        df_fix_leg = [cf.discount_index.get_value(cf.pay_date, value_date) for cf in fix_list]
        annuity = sum([df * cf.year_fraction * abs(cf.notional) for df, cf in zip(df_fix_leg, fix_list)])

        fair_rate = pv_float_leg / annuity
        return fair_rate


class CashFlowListIRSwap(InterestRateSwap):
    """ InterestRateSwap defined by CashFLowLists """

    @property
    def leg_list(self):
        """ list of cashflow lists """
        return self._rec_cash_flow_list_, self._pay_cash_flow_list_

    def __init__(self, object_name_str=''):
        super(CashFlowListIRSwap, self).__init__(object_name_str)
        self._rec_cash_flow_list_ = CashFlowList()
        self._pay_cash_flow_list_ = CashFlowList()


class LegListIRSwap(InterestRateSwap):
    """ InterestRateSwap defined by CashFLowLegLists """

    @property
    def leg_list(self):
        """ leg list """
        return tuple(l.cashflow_list for l in self._leg_list_)

    def __init__(self, object_name_str=''):
        super(LegListIRSwap, self).__init__(object_name_str)
        self._leg_list_ = CashFlowLegList()

    def _rebuild_object(self):
        for leg in self.leg_list:
            for cf in leg:
                cf._rebuild_object()
