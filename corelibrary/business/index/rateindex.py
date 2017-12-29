# coding=utf-8
"""
defining index
"""
from businessdate import BusinessDate, BusinessPeriod

from corelibrary.analytics.model.indexmodel import InterestRateIndexModel, DiscountIndexModel, CashRateIndexModel

from corelibrary.base.namedobject import TAR, Act360, Simple, ModFollow

from baseindex import Index


class RateIndex(Index):
    """ base rate index """

    @property
    def xyieldcurve(self):
        """ depending YieldCurve """
        return self._index_model_._curve_

    @property
    def xvol(self):
        """ volatility """
        return self._index_model_._vol_

    @property
    def tenor(self):
        """ tenor, i.e. time period, of index underlying """
        return self._tenor_

    def __init__(self, object_name_str=''):
        super(RateIndex, self).__init__(object_name_str)
        self._index_model_ = InterestRateIndexModel()

        self._calendar_ = TAR()
        self._spot_ = BusinessPeriod(businessdays=2, holiday=self._calendar_)
        self._tenor_ = BusinessPeriod(months=6, holiday=self._calendar_)
        self._day_count_ = Act360()
        self._compounding_ = Simple()
        self._rolling_method_ = ModFollow()
        self._rolling_method_.holidays = self._calendar_

    def _rebuild_object(self):
        super(RateIndex, self)._rebuild_object()
        if "Calendar" in self._modified_members:
            self._rolling_method_.holidays = self._calendar_

    def _rate_start_date(self, reset_date):
        """

        :param BuisnessDate reset_date:
        :return: BuisnessDate
        """
        spot = BusinessPeriod(self._spot_, self._calendar_)
        return reset_date.add_period(spot)  # todo shouldn't we adjust reset_date, too?

    def _rate_end_date(self, reset_date):
        """

        :param BuisnessDate _rate_start_date:
        :return: BuisnessDate
        """
        tenor = BusinessPeriod(self._tenor_, self._calendar_)
        start = self._rate_start_date(reset_date).add_period(tenor)
        return self._rolling_method_.adjust(start, self._calendar_)


class DiscountIndex(RateIndex):
    """ DiscountIndex """

    def __init__(self, object_name_str=''):
        super(DiscountIndex, self).__init__(object_name_str)
        self._index_model_ = DiscountIndexModel()


class ZeroBondIndex(DiscountIndex):
    """ ZeroBondIndex """
    pass


class CashRateIndex(RateIndex):
    """ cash rate (LIBOR) index """

    def __init__(self, object_name_str=''):
        super(CashRateIndex, self).__init__(object_name_str)
        self._index_model_ = CashRateIndexModel()


class OverNightRateIndex(RateIndex):
    """ over night index rate index """
    def __init__(self, object_name_str=''):
        super(OverNightRateIndex, self).__init__(object_name_str)
        self._tenor_ = BusinessPeriod(days=1)

    def _rebuild_object(self):
        if self._is_modified_property("_tenor_"):
            t = self._tenor_
            if not (t.businessdays, t.years, t.months, t.days) == (0, 0, 0, 1):
                raise Exception("Invalid tenor " + str(self._tenor_) + " for a OverNightRateIndex")
