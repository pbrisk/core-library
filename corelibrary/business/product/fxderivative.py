# coding=utf-8

from businessdate import BusinessDate
from mitschreiben import Record

from corelibrary.base.interface.payoff import PayOffInterface
from corelibrary.base.namedobject import USD, Call, Put
from corelibrary.business.index import FXIndex, FXValueInv, ZeroBondIndex

from basederivative import SwapProduct, Option, Forward


class FxOutright(Forward):
    """ FxOutright """
    pass


class FxSwap(SwapProduct):
    """ FxSwap """
    pass


class FxOption(Option, PayOffInterface):
    """ FxOption """

    @property
    def strike_ccy(self):
        return self._underlying_.domestic_currency

    @property
    def pay_date(self):
        return self._settlement_date_

    def __init__(self, object_name_str=''):
        super(FxOption, self).__init__(object_name_str)
        self._underlying_ = FXIndex()  # why two FXIndices()
        self._f_x_index_ = FXIndex()   # why two FXIndices()
        self._strike_ = 1.1
        self._pay_currency_ = USD()
        self._pay_discount_index_ = ZeroBondIndex()

    def get_expected_payoff(self, value_date=BusinessDate(), index_model_dict={}):
        """ calculates expected payoff at paydate

        :param BusinessDate value_date:
        :param IndexModel index_model_dict:
        :return: float, the pv of the cash flow
        """
        idx_model = index_model_dict.get(self._underlying_.object_name, self._underlying_._index_model_)

        def _prepare_return(self, value, vol, time, forward):
            possign = self._position_sign()
            payoff = self._notional_ * possign * value
            #pv = self._get_discounted_value(value_date, payoff, self._underlying_.domestic_currency)
            Record(
                expected_payoff=payoff,
                opt_value=value,
                vol=vol,
                time=time,
                forward=forward,
                strike=self._strike_,
                position_sign=possign,
                notional=self._notional_,
                pay_ccy=self._pay_currency_
            )
            return payoff

        if self._exercise_date_ <= value_date: # option already exercised.
            return _prepare_return(self, 0.0, 0.0, 0.0, 0.0)

        if self._option_type_ == Call():
            value, vol, time, fwd = idx_model.get_option_payoff_value(self._underlying_,
                                                                      Call(),
                                                                      self._strike_,
                                                                      self._exercise_date_)
            return _prepare_return(self, value, vol, time, fwd)

        elif self._option_type_ == Put():
            value, vol, time, fwd = idx_model.get_option_payoff_value(self._underlying_,
                                                                      Put(),
                                                                      self._strike_,
                                                                      self._exercise_date_)
            return _prepare_return(self, value, vol, time, fwd)

        raise Exception("Invalid OptionType '" + str(self._option_type_) + "'.")

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """
        :param BusinessDate value_date:
        :param IndexModel index_model_dict:
        :return: float, the pv of the cash flow
        """
        payoff = self.get_expected_payoff(value_date, index_model_dict)

        fx_index = self._get_fx_index(self._underlying_.domestic_currency)
        df_index = self._get_discount_index(self._underlying_.domestic_currency)

        fx = fx_index.get_value(value_date) if fx_index else 1.0
        pv_let = self._get_discounted_value(value_date, payoff, df_index)

        return pv_let * fx

    def _position_sign(self):
        return 1.0 if self._position_ == "Long" else -1.0

    def _get_fx_index(self, currency, default=None):
        def _get_fx_index():
            if self._is_modified_property('_f_x_index_'):
                return self._f_x_index_
            else:
                return FXValueInv(self._underlying_)

        if self.currency == currency:
            return FXIndex()
        else:
            fx_idx = _get_fx_index()
            return fx_idx


class FxBarrierType(object):  # fixme: should be NamedObject
    UP_IN = "UpIn"
    UP_OUT = "UpOut"
    DOWN_IN = "DownIn"
    DOWN_Out = "DownOut"


class FxBarrierOption(FxOption):
    """ FxBarrierOption """
    def __init__(self, object_name_str=''):
        super(FxBarrierOption, self).__init__(object_name_str)
        self._barrier_start_date_ = self._origin_
        self._barrier_end_date_ = self._exercise_date_
        self._barrier_ = 1.4
        self._barrier_type_ = 'Continuous'
        self._barrier_rebate_ = 0.0
        self._barrier_rate_coupon_ = 0.0
        self._barrier_option_type_ = FxBarrierType.UP_IN  # fixme: should use NamedObject


class FxDoubleBarrierOption(FxOption):
    """ FxDoubleBarrierOption """
    def __init__(self, object_name_str=''):
        super(FxDoubleBarrierOption, self).__init__(object_name_str)

        self._barrier_start_date_ = self._origin_
        self._barrier_end_date_ = self._exercise_date_
        self._upper_barrier_ = 1.1
        self._lower_barrier_ = 0.9
        self._lower_barrier_type_ = 'Continuous'
        self._upper_barrier_type_ = 'Continuous'
        self._lower_barrier_rebate_ = 0.0
        self._upper_barrier_rebate_ = 0.0
        self._barrier_rate_coupon_ = 0.0
        self._upper_barrier_option_type = "None"
        self._lower_barrier_option_type = "None"

