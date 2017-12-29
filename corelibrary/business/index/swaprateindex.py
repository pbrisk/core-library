from businessdate import BusinessDate, BusinessPeriod

from corelibrary.analytics.model.indexmodel import SwapRateIndexModel

from corelibrary.base.interface.index import SwapRateIndexInterface
from corelibrary.base.namedobject import TAR, Act360, D30360, ModFollow
from corelibrary.business.product import LegListIRSwap, CashFlowLeg, CashFlowLegList

from rateindex import RateIndex, ZeroBondIndex


class SwapRateBaseIndex(RateIndex, SwapRateIndexInterface):
    """ swap rate index base, defines methods for the a swap rate index. """

    def __init__(self, object_name_str=''):
        super(SwapRateBaseIndex, self).__init__(object_name_str)
        self._index_model_ = SwapRateIndexModel()

    def get_underlying_swap(self, reset_date):
        return NotImplemented


class SwapRateIndex(SwapRateBaseIndex):
    """ swap rate (ISDAFIX) index """

    @property
    def discount_index(self):
        return self._discount_index_

    def __init__(self, object_name_str=''):
        super(SwapRateIndex, self).__init__(object_name_str)
        self._calendar_ = TAR()
        self._tenor_ = BusinessPeriod(years=5)
        self._rolling_frequency_ = BusinessPeriod(years=1)
        self._rolling_method_ = ModFollow()
        self._accrued_day_count_ = D30360()
        self._rate_index_ = RateIndex()
        self._float_rolling_frequency_ = BusinessPeriod(months=6)
        self._float_rolling_method_ = ModFollow()
        self._float_accrued_day_count_ = Act360()
        self._reset_offset_ = self._rate_index_._spot_
        self._discount_index_ = ZeroBondIndex()
        self._payer_receiver_ = "Payer"

    def _rebuild_object(self):
        super(SwapRateIndex, self)._rebuild_object()
        if not self._is_modified_property('_reset_offset_'):
            self._reset_offset_ = self._rate_index_._spot_
        else:
            self._reset_offset_.holiday = self._rate_index_._spot_.holiday

    def get_underlying_swap(self, reset_date):
        """ underlying swap

        :param reset_date:
        :return: InterestRateSwap
        """
        start_date = reset_date.add_period(self._reset_offset_)

        fix_leg = CashFlowLeg.create(
            'FixLeg',
            PayRec='Pay' if self._payer_receiver_.upper() == "PAYER" else 'Rec',
            Currency=self._currency_,
            Notional=1e4,
            StartDate=self._rolling_method_.adjust(start_date, self._calendar_),
            EndDate=start_date.add_period(self._tenor_),
            RollingFrequency=self._rolling_frequency_,
            AccruedDayCount=self._accrued_day_count_,
            RollingMethod=self._rolling_method_,
            RollingCalendar=self._calendar_,
            ConstantRate=.01,
            DiscountIndex=self._discount_index_
        )

        float_leg = CashFlowLeg.create(
            'FloatLeg',
            PayRec='Rec' if self._payer_receiver_.upper() == "PAYER" else 'Pay',
            Currency=self._currency_,
            Notional=1e4,
            StartDate=self._rolling_method_.adjust(start_date, self._calendar_),
            EndDate=start_date.add_period(self._tenor_),
            RollingFrequency=self._float_rolling_frequency_,
            AccruedDayCount=self._float_accrued_day_count_,
            RollingMethod=self._float_rolling_method_,
            RollingCalendar=self._calendar_,
            ResetOffset=self._reset_offset_,
            RateIndex=self._rate_index_,
            DiscountIndex=self._discount_index_
        )

        underlying = LegListIRSwap.create(
            '',
            LegList=CashFlowLegList([fix_leg, float_leg]),
            Currency= self._currency_,
            DiscountIndex=self._discount_index_
        )

        fix_rate = underlying.get_fair_rate(start_date)
        underlying.fix_leg.modify_object('ConstantRate', fix_rate)
        return underlying


class SwapProductIndex(SwapRateBaseIndex):
    """ A swap rate index with an underlying swap product, discountcurve and swaption vol. """

    @property
    def discount_index(self):
        return self._underlying_swap_.discount_index

    def __init__(self, object_name_str=''):
        super(SwapProductIndex, self).__init__(object_name_str)
        self._underlying_swap_ = LegListIRSwap()

    def get_underlying_swap(self, reset_date):
        """ underlying swap

        :param reset_date:
        :return: InterestRateSwap
        """
        return self._underlying_swap_
