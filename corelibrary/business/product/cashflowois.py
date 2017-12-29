# coding=utf-8
from businessdate import BusinessDate
from mitschreiben import Record

from cashflow import CashFlow


class OISCashFlow(CashFlow):
    """ OISCashFlow """

    class OISPayoff(object):
        def __init__(self, curve, fixing_fct, calendar, day_count):
            """

            :param curve: hast to implement the method 'get_discount_factor(start_date, end_date)'
            :param fixing_fct: has to be be callable with date and returns a float value
            :param calendar: a calendar
            :param day_count: has to implement get_year_fraction(date1, date2)
            """
            self._fixing_fct = fixing_fct
            self._curve = curve
            self._calendar = calendar
            self._day_count = day_count

        def calc_payoff(self, value_date, start_date, end_date, day_count_fraction):

            def _payoff(one_over_disc_fact, day_count_fraction_value):
                return (one_over_disc_fact - 1.0) / day_count_fraction_value

            if start_date < value_date:
                floating = self.get_floating_part(value_date, end_date)
                fixed = self.get_fixed_rate_part(start_date, value_date.add_business_days(-1, self._calendar))
                one_over_disc_fact = floating * fixed
                ret = _payoff(one_over_disc_fact, day_count_fraction)
                return ret
            else:
                one_over_disc_fact = self.get_floating_part(start_date, end_date)
                return _payoff(one_over_disc_fact, day_count_fraction)

        def get_floating_part(self, start_date, end_date):
            return 1.0 / self._curve.get_discount_factor(start_date, end_date)

        def ois_dates_dcf(self, start_date, end_date):
            ret = []
            fixing_date = start_date
            while fixing_date <= end_date:
                next = BusinessDate.add_business_days(fixing_date, 1, self._calendar)
                dcf = self._day_count.get_year_fraction(fixing_date, next)
                ret.append((fixing_date, dcf))
                fixing_date = next
            return ret

        def get_fixed_rate_part(self, value_date, end_date):
            dates_and_dcfs = self.ois_dates_dcf(value_date, end_date)
            fixings = self._fixing_fct
            ret = 1.
            for fix_date, dcf in dates_and_dcfs:
                ret *= 1.0 + fixings(fix_date) * dcf
            # ret = prod([1.0 + fixings(fix_date) * dcf for fix_date, dcf in dates_and_dcfs])
            return ret

    class ConstFixing(object):
        def __init__(self, index_obj):
            self._last = None
            self._index = index_obj

        def __call__(self, fixing_date):
            fix = self._index.get_fixing(fixing_date)
            if fix is None:
                return self._last
            else:
                self._last = fix
                return fix

    @Record.Prefix()
    def get_expected_payoff(self, value_date=BusinessDate(), index_model_dict={}):
        """

        :param value_date:
        :param index_model_dict:
        :return:
        """
        payoff = 0.0
        rate = None
        if self._pay_date_ > value_date:
            rate_idx = self._rate_index_
            fixing_fct = OISCashFlow.ConstFixing(rate_idx)
            oispayoff = OISCashFlow.OISPayoff(rate_idx.index_model.yieldcurve, fixing_fct, rate_idx._calendar_,
                                              rate_idx._day_count_)
            rate = oispayoff.calc_payoff(value_date, self._start_date_, self._end_date_, self._year_fraction_)
            rate *= self._multiplier_
            rate += self._spread_
            payoff = rate * self._year_fraction_ * self._notional_ + self._amount_

        Record(
            year_fraction=self.year_fraction,
            cf_name=self.object_name,
            notional=self._notional_,
            currency=self.currency,
            forward=rate,
            spread=self._spread_,
            reset_date=self._reset_date_,
            start_date=self._start_date_,
            end_date=self._end_date_,
            pay_date=self._pay_date_,
            amount=self._amount_,
            index=self._rate_index_.object_name,
            expected_payoff=payoff
        )  # pylint: disable=unexpected-keyword-arg

        return payoff
