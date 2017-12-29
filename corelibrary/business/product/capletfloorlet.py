from businessdate import BusinessDate
from mitschreiben import Record

from corelibrary.base.baseobject import AttributeList
from corelibrary.base.namedobject import Call, Put

from cashflow import CashFlow


class CapletFloorlet(CashFlow):
    """ Caplet/Floorlet abstract base class """

    @Record.Prefix()
    def get_expected_payoff(self, value_date=BusinessDate(), index_model_dict={}):
        """ calculates expected payoff at paydate

        :param BusinessDate value_date:
        :param IndexModel index_model_dict:
        :return: float, the pv of the cash flow
        """
        idx_model = index_model_dict.get(self._rate_index_.object_name, self._rate_index_.index_model)

        payoff = 0.0
        is_fixed_cash_flow = False
        fwd = None
        fixing_value = None
        time = None
        vol = None
        strike = self._get_strike_value()
        effective_strike = (strike - self._spread_) / self._multiplier_
        pay_rec = 1.0 if self._notional_ >= 0.0 else -1.0
        rate_ccy = self._rate_index_.currency

        if self._pay_date_ > value_date:
            if self._rate_index_.has_fixing(self._reset_date_):
                is_fixed_cash_flow = True
                fixing_value = self._rate_index_.get_fixing(self._reset_date_)
                rate = self._payoff(fixing_value, effective_strike)
            else:
                rate, vol, time, fwd = self._get_option_value(idx_model, effective_strike)

            rate *= self._multiplier_
            rate += self._spread_
            payoff = rate * self._year_fraction_ * self._notional_ + self._amount_

        Record(
            pay_rec="REC" if pay_rec == 1.0 else "PAY",
            year_fraction=self.year_fraction,
            cf_name=self.object_name,
            notional=self._notional_,
            currency=self.currency,
            forward=fwd,
            is_fixed_cash_flow=is_fixed_cash_flow,
            fixing_value=fixing_value,
            vol=vol,
            expiry_time=time,
            spread=self._spread_,
            reset_date=self._reset_date_,
            start_date=self._start_date_,
            end_date=self._end_date_,
            pay_date=self._pay_date_,
            constant_rate=self._constant_rate_,
            amount=self._amount_,
            strike=strike,
            effective_strike=effective_strike,
            index=self._rate_index_.object_name,
            expected_payoff=payoff,
            rate_ccy=rate_ccy
        )  # pylint: disable=unexpected-keyword-arg

        return payoff


class Caplet(CapletFloorlet):
    """ Caplet """

    def _payoff(self, fixing_value, strike):
        return max(fixing_value - strike, 0.0)

    def _get_option_value(self, index_model_object, strike):
        return index_model_object.get_option_payoff_value(self._rate_index_, Call(), strike, self._reset_date_)

    def _get_strike_value(self):
        return self._cap_


class Floorlet(CapletFloorlet):
    """ Floorlet """

    def _payoff(self, fixing_value, strike):
        return max(strike - fixing_value, 0.0)

    def _get_option_value(self, index_model_object, strike):
        return index_model_object.get_option_payoff_value(self._rate_index_, Put(), strike, self._reset_date_)

    def _get_strike_value(self):
        return self._floor_


class CapletList(AttributeList):
    """
    specific AttributeList for Caplets
    """

    def __init__(self, iterable=None):
        super(CapletList, self).__init__(iterable, object_type=Caplet)


class FloorletList(AttributeList):
    """
    specific AttributeList for Floorlets
    """

    def __init__(self, iterable=None):
        super(FloorletList, self).__init__(iterable, object_type=Floorlet)
