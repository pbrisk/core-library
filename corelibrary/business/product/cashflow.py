# coding=utf-8
""" defining CashFlow and CashFlowLeg """

from businessdate import BusinessDate, BusinessPeriod, BusinessSchedule
from mitschreiben import Record

from corelibrary.base.baseobject import AttributeList
from corelibrary.base.interface.payoff import PayOffInterface
from corelibrary.base.namedobject import Act360, ModFollow, TAR
from corelibrary.base.namedobject import Call, Put
from corelibrary.business.index import CashRateIndex

from baseproduct import Product

# more classical than useful plains
NO_CAP_VALUE = 9.99
NO_FLOOR_VALUE = -9.99


class CashFlow(PayOffInterface, Product):
    """ representation of a single cash flow with all the necessary dates and the index for calculation of the rate """

    @property
    def rate_index(self):
        """ float rate index of cash flow """
        return self._rate_index_

    @property
    def start_date(self):
        """ start date of accrual period """
        return self._start_date_

    @property
    def end_date(self):
        """ end date of accrual period """
        return self._end_date_

    @property
    def reset_date(self):
        """ reset date , i.e. fixing date, of cash flow index """
        return self._reset_date_

    @property
    def pay_date(self):
        """ cash flow pay date """
        return self._pay_date_

    @property
    def year_fraction(self):
        """ year fraction of accrual period """
        return self._year_fraction_

    @property
    def is_pay(self):
        """ True if leg pays, False if leg receives """
        return self._notional_ < 0.

    @property
    def is_rec(self):
        """ False if leg pays, True if leg receives """
        return not self.is_pay

    @property
    def is_fix(self):
        """ True if CashFlow has non zero ConstantRate """
        return True if self._constant_rate_ else False

    @property
    def is_float(self):
        """ True if CashFlow has zero ConstantRate """
        return not self.is_fix

    def __init__(self, object_name_str=''):
        super(CashFlow, self).__init__(object_name_str)

        # index property
        self._rate_index_ = CashRateIndex()

        # rate calc properties
        self._start_date_ = BusinessDate()
        self._end_date_ = BusinessDate.add_period(self._start_date_, self._rate_index_.tenor)

        self._accrued_day_count_ = Act360()
        self._year_fraction_ = self._accrued_day_count_.get_year_fraction(self._start_date_, self._end_date_)

        self._reset_date_ = self._start_date_ - self._rate_index_._spot_
        self._pay_date_ = BusinessDate.add_period(self._end_date_, self._rate_index_._spot_)

        # payoff properties
        self._spread_ = 0.00
        self._constant_rate_ = 0.0
        self._amount_ = 0.00
        self._multiplier_ = 1.00
        self._cap_ = NO_CAP_VALUE
        self._floor_ = NO_FLOOR_VALUE

        self._rebuild_object()

    def _rebuild_object(self):
        # check which dates etc are not modified members -> rebuild them
        if '_reset_date_' not in self._modified_members:
            self._reset_date_ = self._start_date_ - self._rate_index_._spot_

        if '_end_date_' not in self._modified_members:
            if '_year_fraction_' in self._modified_members:
                yf = self._year_fraction_
                e = self._start_date_.add_days(int(yf * 365.25))
                my_yf = self._accrued_day_count_.get_year_fraction(self._start_date_, e)
                while yf < my_yf:
                    e -= '1d'
                    my_yf = self._accrued_day_count_.get_year_fraction(self._start_date_, e)
                while yf > my_yf:
                    e += '1d'
                    my_yf = self._accrued_day_count_.get_year_fraction(self._start_date_, e)
                self._end_date_ = e
            else:
                self._end_date_ = BusinessDate.add_period(self._start_date_, self._rate_index_.tenor)
                self._end_date_ = self._rate_index_._rolling_method_.adjust(self._end_date_)

        if '_pay_date_' not in self._modified_members:
            self._pay_date_ = BusinessDate.add_period(self._end_date_, self._rate_index_._spot_)
            self._pay_date_ = self._rate_index_._rolling_method_.adjust(self._pay_date_)

        if '_year_fraction_' not in self._modified_members:
            self._year_fraction_ = self._accrued_day_count_.get_year_fraction(self._start_date_, self._end_date_)

        # validate
        if '_year_fraction_' in self._modified_members and '_end_date_' in self._modified_members:
            yf = self._accrued_day_count_.get_year_fraction(self._start_date_, self._end_date_)
            # if not float_equal(yf, self._year_fraction_, 0.00000001):
            if not abs(yf - self._year_fraction_) < 0.00000001:
                s = self.__class__.__name__
                # raise ValueError('If %s.YearFraction and %s.EndDate is given they must meet.' % (s, s))

        if self._end_date_ < self._start_date_:
            s = self.__class__.__name__, self._end_date_, self.__class__.__name__, self._start_date_
            raise ValueError('%s.EndDate (%s) must scheduled after %s.StartDate (%s).' % s)

        if self._year_fraction_ > 0 and self._pay_date_ <= self._reset_date_:
            s = self.__class__.__name__, self._pay_date_, self.__class__.__name__, self._reset_date_
            raise ValueError('%s.PayDate (%s) must scheduled after %s.SetDate (%s).' % s)

        return self

    def get_expected_payoff(self, value_date=BusinessDate(), index_model_dict={}):
        """ calculates expected payoff at paydate

        :param BusinessDate value_date:
        :param IndexModel index_model_dict:
        :return: float, the pv of the cash flow
        """
        idx_model = index_model_dict.get(self._rate_index_.object_name, self._rate_index_.index_model)
        rate = 0.0
        is_fix_rate = True
        is_fixed_cash_flow = False
        fwd = None
        fixing_value = None
        time = None
        vol = None
        effective_floor_strike = None
        effective_cap_strike = None
        pay_rec = 1.0 if self.is_rec else -1.0
        payoff = 0.0
        rate_ccy = self.currency

        if self._pay_date_ > value_date:
            if self._constant_rate_:
                rate += self._constant_rate_
            else:
                is_fix_rate = False  # fixme: be consistent, use is_fixed_flow?
                rate_ccy = self._rate_index_.currency

                if self._rate_index_.has_fixing(self._reset_date_):
                    is_fixed_cash_flow = True
                    fixing_value = self._rate_index_.get_fixing(self._reset_date_)
                    rate = fixing_value
                else:
                    fwd = idx_model.get_value(self._rate_index_, self._reset_date_, self._pay_date_)
                    rate = fwd

                if self._floor_ != NO_FLOOR_VALUE:
                    effective_floor_strike = (self._floor_ - self._spread_) / self._multiplier_
                    if not is_fixed_cash_flow:
                        value, vol, time, fwd = idx_model.get_option_payoff_value(self._rate_index_,
                                                                                  Put(),
                                                                                  effective_floor_strike,
                                                                                  self._reset_date_)
                    else:
                        value = max(effective_floor_strike - rate, 0)
                    rate += value

                if self._cap_ != NO_CAP_VALUE:
                    effective_cap_strike = (self._cap_ - self._spread_) / self._multiplier_
                    if not is_fixed_cash_flow:
                        value, vol, time, fwd = idx_model.get_option_payoff_value(self._rate_index_,
                                                                                  Call(),
                                                                                  effective_cap_strike,
                                                                                  self._reset_date_)
                    else:
                        value = max(rate - effective_cap_strike, 0)
                    rate -= value

                rate *= self._multiplier_
                rate += self._spread_

            fx_index = self._get_fx_index(self.currency)
            fx = fx_index.get_value(value_date) if fx_index else 1.0

            payoff = fx * rate * self._year_fraction_ * self._notional_ + self._amount_

        Record(
            pay_rec="REC" if pay_rec == 1.0 else "PAY",
            year_fraction=self.year_fraction,
            cf_name=self.object_name,
            notional=self._notional_,
            currency=self.currency,
            rate_ccy=rate_ccy,
            is_fix_rate=is_fix_rate,
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
            effective_floor_strike=effective_floor_strike,
            effective_cap_strike=effective_cap_strike,
            index=self._rate_index_.object_name,
            expected_payoff=payoff,
            floor=None if self._floor_ == NO_FLOOR_VALUE else self._floor_,
            cap=None if self._cap_ == NO_CAP_VALUE else self._cap_
        )  # pylint: disable=unexpected-keyword-arg

        return payoff

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """
        :param BusinessDate value_date:
        :param IndexModel index_model_dict:
        :return: float, the pv of the cash flow
        """
        payoff = self.get_expected_payoff(value_date, index_model_dict)
        df_index = self._get_discount_index(self.currency)

        pv_let = self._get_discounted_value(value_date, payoff, df_index)
        return pv_let


class FloatCashFlow(CashFlow):
    """ float rate cashflow """

    @property
    def is_fix(self):
        """ False """
        return False


class FixCashFlow(CashFlow):
    """ fixed rate cashflow """

    @property
    def is_fix(self):
        """ True """
        return True

    def get_expected_payoff(self, value_date=BusinessDate(), index_model_dict={}):
        """ calculates expected payoff at paydate

        :param BusinessDate value_date:
        :param IndexModel index_model_dict:
        :return: float, the pv of the cash flow
        """
        rate = 0.0
        is_fix_rate = True
        is_fixed_cash_flow = False
        fwd = None
        fixing_value = None
        time = None
        vol = None
        effective_floor_strike = None
        effective_cap_strike = None
        pay_rec = 1.0 if self._notional_ >= 0.0 else -1.0
        payoff = 0.0
        rate_ccy = self.currency

        if self._pay_date_ > value_date:
            rate += self._constant_rate_

            fx_index = self._get_fx_index(self.currency)
            fx = fx_index.get_value(value_date) if fx_index else 1.0

            payoff = fx * rate * self._year_fraction_ * self._notional_ + self._amount_

        Record(
            pay_rec="REC" if pay_rec == 1.0 else "PAY",
            year_fraction=self.year_fraction,
            cf_name=self.object_name,
            notional=self._notional_,
            currency=self.currency,
            rate_ccy=rate_ccy,
            is_fix_rate=is_fix_rate,
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
            effective_floor_strike=effective_floor_strike,
            effective_cap_strike=effective_cap_strike,
            index=self._rate_index_.object_name,
            expected_payoff=payoff,
            floor=None if self._floor_ == NO_FLOOR_VALUE else self._floor_,
            cap=None if self._cap_ == NO_CAP_VALUE else self._cap_
        )  # pylint: disable=unexpected-keyword-arg

        return payoff


class CashFlowList(AttributeList):
    """ specific AttributeList for CashFlows """

    @property
    def start_date(self):
        """ start date of accrual period """
        if self:
            return min(cf.start_date for cf in self)

    @property
    def end_date(self):
        """ end date of accrual period """
        if self:
            return min(cf.end_date for cf in self)

    @property
    def is_pay(self):
        """ True if leg pays, False if leg receives """
        pay_cashflows = [cf for cf in self if cf.is_pay]
        rec_cashflows = [cf for cf in self if cf.is_rec]

        if pay_cashflows and not rec_cashflows:
            return True
        elif not pay_cashflows and rec_cashflows:
            return False
        else:
            raise TypeError('CashFlowList.is_pay fails since list contains as well pay as rec CashFlows.')

    @property
    def is_rec(self):
        """ False if leg pays, True if leg receives """
        return not self.is_pay

    @property
    def is_fix(self):
        """ True if leg has only fix flows else False """
        fix_cashflows = [cf for cf in self if cf.is_fix]
        float_cashflows = [cf for cf in self if cf.is_float]

        if fix_cashflows and not float_cashflows:
            return True
        elif not fix_cashflows and float_cashflows:
            return False
        else:
            raise TypeError('CashFlowList.is_pay fails since list contains as well fix as float CashFlows.')

    @property
    def is_float(self):
        """ False if leg has only float flows else True """
        return not self.is_fix

    def __init__(self, iterable=None):
        super(CashFlowList, self).__init__(iterable, object_type=CashFlow)


class CashFlowLeg(Product):
    """ representation of a leg of cash flows """

    @property
    def cashflow_list(self):
        """ list of cash flow """
        return self._cashflow_list_

    @property
    def rate_index(self):
        """ float rate index of cash flow """
        return self._rate_index_

    @property
    def start_date(self):
        """ start date of accrual period """
        return self.cashflow_list.start_date

    @property
    def end_date(self):
        """ end date of accrual period """
        return self.cashflow_list.end_date

    @property
    def is_pay(self):
        """ True if leg pays, False if leg receives """
        return self.cashflow_list.is_pay

    @property
    def is_rec(self):
        """ False if leg pays, True if leg receives """
        return self.cashflow_list.is_pay

    @property
    def is_fix(self):
        """ True if leg has only fix flows else False """
        return self.cashflow_list.is_fix

    @property
    def is_float(self):
        """ False if leg has only float flows else True """
        return self.cashflow_list.is_float

    def __init__(self, object_name_str=''):
        """
        list of the cash flows in this leg,
        reconstructed in _rebuild_object with every change of an object attribute
        """
        super(CashFlowLeg, self).__init__(object_name_str)
        # cash flow list property (new for CashFlowList)
        self._cashflow_list_ = CashFlowList()

        # index property (same for CashFlow)
        self._rate_index_ = CashRateIndex()

        # payoff properties (new for CashFlowLeg)
        self._pay_rec_ = "Pay" if self._notional_ >= 0. else "Rec"

        # schedule properties (same for CashFlow)
        self._start_date_ = BusinessDate()

        # self.SetDate  replaced by ResetOffset
        self._end_date_ = BusinessDate.add_period(self._start_date_, self.rate_index.tenor)
        # self._pay_date_  replaced by PayOffset

        # roll properties (new for CashFlowLeg)
        self._rolling_date_ = self._end_date_
        self._rolling_frequency_ = self.rate_index.tenor
        self._rolling_method_ = ModFollow()
        self._rolling_calendar_ = TAR()

        self._reset_offset_ = self.rate_index._spot_
        self._reset_method_ = self._rolling_method_
        self._reset_calendar_ = self._rolling_calendar_

        self._pay_offset_ = BusinessPeriod(businessdays=0)
        self._pay_method_ = self._rolling_method_
        self._pay_calendar_ = self._rolling_calendar_

        # payoff properties (same for CashFlow)
        self._spread_ = 0.00
        self._constant_rate_ = 0.0
        self._amount_ = 0.00
        self._multiplier_ = 1.00
        self._cap_ = NO_CAP_VALUE
        self._floor_ = NO_FLOOR_VALUE
        self._accrued_day_count_ = Act360()
        # self.YearFraction  calculated in CashFlow

        self._rebuild_object()

    def _rebuild_schedules(self):
        bs = self._start_date_, self._end_date_, self._rolling_frequency_, self._rolling_date_
        u = BusinessSchedule(*bs)
        a = [self._rolling_method_.adjust(d, self._rolling_calendar_) for d in u]
        start = a[:-1]
        end = a[1:]
        reset = [self._reset_method_.adjust(d - self._reset_offset_, self._reset_calendar_) for d in start]
        pay = [self._pay_method_.adjust(d + self._pay_offset_, self._pay_calendar_) for d in end]
        return start, end, reset, pay

    def _rebuild_cash_flows(self):
        # clear CashFlowList
        self._cashflow_list_ = CashFlowList()
        # collect common properties
        prop_name = list()
        # collect Product property names
        prop_name.extend(['_notional_', '_currency_', '_discount_index_'])
        # collect CashFlow payoff property names
        prop_name.extend(['_rate_index_', '_spread_', '_constant_rate_', '_amount_'])
        prop_name.extend(['_multiplier_', '_cap_', '_floor_', '_accrued_day_count_'])
        # collect property values
        prop_value = [getattr(self, p) for p in prop_name]

        # create CashFlows
        for start, end, reset, pay in zip(*self._rebuild_schedules()):
            name = self.object_name, str(self._notional_), str(start), self.rate_index.object_name
            cf = CashFlow('-'.join(name))
            # collect CashFlow schedule properties and modify object
            cf.modify_object(prop_name + ['_start_date_', '_end_date_', '_reset_date_', '_pay_date_'],
                             prop_value + [start, end, reset, pay])
            self._cashflow_list_.append(cf)

    def _rebuild_object(self):
        super(CashFlowLeg, self)._rebuild_object()
        # setup PayRec mechanics. If PayRec given Notional must be non negative to adjust sign
        if '_pay_rec_' not in self._modified_members:
            self._pay_rec_ = 'Pay' if self._notional_ < 0.0 else 'Rec'
        else:
            if '_notional_' in self._modified_members and self._notional_ < 0.0:
                # s = self.__class__.__name__
                # raise ValueError("When using %s.PayRec property %s.Notional must be non negative" % (s, s))
                self._notional_ *= 1.0 if self._pay_rec_.upper() == 'PAY' else -1.0
            else:
                self._notional_ *= -1.0 if self._pay_rec_.upper() == 'PAY' else 1.0
        # handle dates
        if '_rolling_date_' not in self._modified_members:
            self._rolling_date_ = self._end_date_

        # now rebuild CashFlow schedule
        if '_cashflow_list_' not in self._modified_members:
            self._rebuild_cash_flows()

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns present value at value_date derived by given index_models if provided

        :param value_date:
        :param index_model_dict:
        :return:
        """

        return self._get_present_value_sum(self._cashflow_list_, value_date, index_model_dict)


class CashFlowLegList(AttributeList):
    """ AttributeList for CashFlowLegs """

    def __init__(self, iterable=None, object_type=CashFlowLeg):
        super(CashFlowLegList, self).__init__(iterable, object_type=object_type)
