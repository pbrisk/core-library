# coding=utf-8
""" module define collateral lists """
from businessdate import BusinessDate, BusinessSchedule

from corelibrary.base.namedobject.frequency import Monthly
from corelibrary.base.namedobject.compounding import Annually as AnnuallyCompounding
from corelibrary.base.namedobject.daycount import ActAct
from corelibrary.business.index import AssetIndex, RecoveryIndex
from corelibrary.business.party import Party

from basederivative import Option
from baseproduct import Product


class CollateralProduct(Product):
    """ Collateral Product super class """

    @property
    def prior_charge(self):
        """ senior amount (prior charge) """
        return self._prior_charge_

    @property
    def max_claim(self):
        """ senior amount (prior charge) """
        return self._max_claim_

    def __init__(self, object_name_str=''):
        super(CollateralProduct, self).__init__(object_name_str)
        self._max_claim_ = 0.
        self._prior_charge_ = 0.


class Mortgage(CollateralProduct):
    """ Collateral Product of a mortgage where real estate evolution is considered. """

    def __init__(self, object_name_str=''):
        super(Mortgage, self).__init__(object_name_str)
        self._mortgage_value_ = 0.
        self._mortgage_value_date_ = BusinessDate()
        self._asset_index_ = AssetIndex()
        self._recovery_index_ = RecoveryIndex()

    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        r"""
        The forward value at time :math:`t`, i.e. :math:`S_t`, is calculated
        by the minimum of the expected future mortgage value and the
        mortgage amount such that

        .. math::
            S_t = S_0 \cdot e^{\mu t}

        where :math:`S_0` is the current mortgage value and  :math:`\mu`
        the rate of return for real estate evolution.
        """
        pv_0 = self._mortgage_value_ * self._asset_index_.get_value(self._mortgage_value_date_, self.origin)
        pv_t = pv_0 * self._asset_index_.get_value(value_date)
        return pv_t * self._discount_index_.get_value(value_date)


class BuildingSavingsAccount(CollateralProduct):
    """ Collateral Product of a savings contract where annual expected saving rates and interests are considered. """

    def __init__(self, object_name_str=''):
        super(BuildingSavingsAccount, self).__init__(object_name_str)
        self._day_count_ = ActAct
        self._current_amount_ = 0.
        self._savings_amount_ = 0.
        self._savings_frequency_ = Monthly()
        self._savings_interest_rate_ = 0.
        self._end_date_ = self.origin

    def _rebuild_object(self):
        self._schedule = BusinessSchedule(self.origin, self._end_date_, self._savings_frequency_.period)
        return self

    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        r""" returns the forward value of building savings account

        Parameters:
            value_date (BusinessDate): date of the valuation

        Return:
            (float): forward value of a financial security

        The forward value at time :math:`t`, i.e. :math:`S_t`, is calculated by

        .. math::
            :nowrap:

            \[
                 S_t = S_0 e^{\mu t} + 12 \cdot CF
                       \left( \frac{(1+r_S)^{t+1}-1}{r_S}-1 \right)
            \]

        where :math:`S_0` reflects the current savings amount, :math:`CF` constant
        expected future monthly savings amount and :math:`r_S` is the contractual
        savings interest rate.
        """

        dcc = self._day_count_
        rate = self._savings_interest_rate_

        df = AnnuallyCompounding().disc_factor_from_rate(self.origin, value_date, dcc, rate)
        expected_notional = self._current_amount_ / df

        for loop_date in self._schedule:
            if loop_date > value_date:
                break
            df = AnnuallyCompounding().disc_factor_from_rate(loop_date, value_date, dcc, rate)
            expected_notional += self._savings_amount_ / df

        return expected_notional * self._discount_index_.get_value(value_date)


class Guarantee(CollateralProduct):
    """ Collateral Product with a constant value under consideration of double default of the guarantor """

    def __init__(self, object_name_str=''):
        super(Guarantee, self).__init__(object_name_str)
        self._guarantee_value_ = 0.
        self._guarantor_ = Party()

    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        r""" returns the forward value

        Parameters:
            value_date (BusinessDate): date of the valuation

        Return:
            (float): forward value of a financial security

        The forward value at time :math:`t`, i.e. :math:`S_t`, is calculated by considering
        double default through the survival probability :math:`S_{GG}(0,t) = 1 - PD_{GG}(0,t)`
        such that

        .. math::
            S_t = G \cdot S_{GG}(0,t)

        where :math:`G` is the guarantee value.
        """

        expected_notional = self._notional_ * self._guarantor_.survival_index.get_value(value_date)
        return expected_notional * self._discount_index_.get_value(value_date)


class FinancialSecurity(CollateralProduct, Option):
    """ Collateral Product with a de-/increase in value by a rate of return. """

    def __init__(self, object_name_str=''):
        super(FinancialSecurity, self).__init__(object_name_str)
        self._asset_value_ = 0
        self._asset_index_ = AssetIndex()

    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        r""" returns the forward value of a financial security

        Parameters:
            value_date (BusinessDate): date of the valuation

        Returns:
            (float): forward value of a financial security

        The forward value at time :math:`t`, i.e. :math:`S_t`,
        is calculated by:

        .. math::
            S_t = S_0 \cdot e^{\mu t}

        where :math:`\mu` is the rate of return
        """

        expected_value = self._asset_value_ * self._asset_index_.get_value(value_date)
        return expected_value * self._discount_index_.get_value(value_date)


class AmortizingCollateral(CollateralProduct):
    """ Collateral Product with amortizing costs, such that the product value is depreciating """

    def __init__(self, object_name_str=''):
        super(AmortizingCollateral, self).__init__(object_name_str)
        self._amortization_date_ = BusinessDate()
        self._acquisition_date_ = BusinessDate()

    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        r""" returns the forward value of a amortizing collateral

        Parameters:
            value_date (BusinessDate): date of the valuation
            value_currency_name (Currency): valueation currrency
            index_model_dict (IndexModel): dict of IndexModel

        Returns:
            (float): forward value of a financial security

        The forward value at time :math:`t`, i.e. :math:`S_t`, is calculated
        by a linear depreciation of the prime costs :math:`AK` such that

        .. math::
            :nowrap:

            \[
                S_t = \max \left( \left(AK \left(1-\frac{t-t_{AK}}
                      {T_{max}}\right) \right),0\right)
            \]

        where :math:`T_{max}` is the maximum amortization BusinessPeriod,
        :math:`t_{AK}` is the time of acquisition.
        """

        s = self._acquisition_date_.to_businessdate(self.origin)
        e = self._amortization_date_.to_businessdate(self.origin)
        t_max = BusinessDate.diff_in_years(s, e)

        v = value_date.to_businessdate(self.origin)
        t = BusinessDate.diff_in_years(s, v)

        expected_value = max(self._notional_ * (1 - (t / t_max)), 0)
        return expected_value * self._discount_index_.get_value(value_date)
