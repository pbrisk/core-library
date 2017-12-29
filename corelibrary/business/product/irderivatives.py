# coding=utf-8

from businessdate import BusinessDate
from mitschreiben.recording import Record

from corelibrary.base.interface.payoff import PayOffInterface
import corelibrary.business.index.swaprateindex  # fixme: from corelibrary.business.index.swaprateindex import SwapRateBaseIndex

from basederivative import Forward, Option, DerivativeProduct
from capletfloorlet import CapletList, FloorletList


class FRA(Forward):
    """ forward rate agreement """
    pass


class IrOption(Option, PayOffInterface):
    """ IR Option """
    pass


class Swaption(IrOption):
    """ European swaption class A swaption with swap (physically) settlement. """

    def __init__(self, object_name_str=''):
        super(Swaption, self).__init__(object_name_str)
        self._underlying_ = corelibrary.business.index.SwapRateBaseIndex()
        self._strike_ = 0.0

    def get_expected_payoff(self, value_date=BusinessDate(), index_model_dict={}):
        """ calculates expected payoff at settlement date

        :param BusinessDate value_date:
        :param IndexModel index_model_dict:
        :return: float, the pv of the cash flow
        """
        idx_model = index_model_dict.get(self._underlying_.object_name, self._underlying_.index_model)

        option_result = idx_model.get_option_payoff_value(self._underlying_,
                                                          self._option_type_,
                                                          self._strike_,
                                                          self._exercise_date_)

        annuity = self._annuity(idx_model, value_date)  # todo: use index_model

        Record(
            vol=option_result[1],
            exercise_time=option_result[2],
            forward=option_result[3],
            annuity=annuity,
            # swap_start_date=fix_cash_flow_list.start_date,
            option_value=option_result[0],
            excersice_date=self._exercise_date_
        )  # pylint: disable=unexpected-keyword-arg

        return option_result[0] * annuity / self._discount_index_.get_value(self._settlement_date_, value_date)

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns present value at value_date derived by given index_models if provided

        :param value_date:
        :param index_model_dict:
        :return:
        """

        pv_value_ccy = self.get_expected_payoff(value_date, index_model_dict)
        fx = 1.0  # fixme: ensure ccy is self.ccy
        pv = fx * pv_value_ccy * self._discount_index_.get_value(self._settlement_date_, value_date)
        return pv

    def _annuity(self, idx_model, value_date):
        return idx_model.get_annuity_value(self._underlying_, self._exercise_date_, value_date, cash=False)


class SwaptionCashSettlement(Swaption):
    """ A european swaption with cash settlement. """

    def _annuity(self, idx_model, value_date):
        return idx_model.get_annuity_value(self._underlying_, self._exercise_date_, value_date, cash=True)


class CapFloor(DerivativeProduct):
    """ cap, floor, collar class """

    @property
    def cashflow_list(self):
        """ list of cash flow """
        return self._get_cash_flow_list()

    def __init__(self, object_name_str=''):
        super(CapFloor, self).__init__(object_name_str)
        self._exclude_1st_period_ = False

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns present value at value_date derived by given index_models if provided

        :param value_date:
        :param index_model_dict:
        :return:
        """
        i0 = 1 if self._exclude_1st_period_ else 0
        cfs = self._get_cash_flow_list()
        pv = self._get_present_value_sum(cfs[i0:], value_date, index_model_dict)
        return pv

    def _get_cash_flow_list(self):
        return []


class Cap(CapFloor):
    """ cap class """

    def __init__(self, object_name_str=''):
        super(Cap, self).__init__(object_name_str)
        self._cap_leg_ = CapletList()

    def _get_cash_flow_list(self):
        return self._cap_leg_


class Floor(CapFloor):
    """ floor class """

    def __init__(self, object_name_str=''):
        super(Floor, self).__init__(object_name_str)
        self._floor_leg_ = FloorletList()

    def _get_cash_flow_list(self):
        return self._floor_leg_
