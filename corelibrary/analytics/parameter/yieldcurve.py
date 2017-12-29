# coding=utf-8
"""
YieldCurve module
"""

from businessdate import BusinessDate, BusinessPeriod
from dcf import ZeroRateCurve, simple_rate

from corelibrary.base.baseobject import DataRange
from corelibrary.base.interface.yieldcurve import YieldCurveInterface
from corelibrary.base.namedobject import TAR, ModFollow, Act360, Continuous, Linear, Constant


class YieldCurve(YieldCurveInterface):
    """ YieldCurve class """

    @property
    def curve(self):
        """ inner curve """
        return self._inner_curve

    @property
    def domain(self):
        """ list of grid date of curve """
        return list(self.curve.domain)

    def __init__(self, object_name_str=''):
        super(YieldCurve, self).__init__(object_name_str)
        self._calendar_ = TAR()
        self._spot_ = BusinessPeriod(businessdays=2, holiday=self._calendar_)
        self._rolling_method_ = ModFollow()
        self._day_count_ = Act360()

        self._compounding_ = Continuous()
        self._rate_type_ = "Zero"
        self._interpolation_ = Linear()
        self._extrapolation_ = Constant()
        self._curve_ = DataRange([['', 'Rate'], [self.origin, 0.0001], [self.origin + '11y', 0.01]])
        self._inner_curve = None

        self._rebuild_object()

    def _rebuild_object(self):
        if self._is_modified_property('_calendar_') and not self._is_modified_property('_spot_'):
            self._spot_ = BusinessPeriod(businessdays=self._spot_.businessdays, holiday=self._calendar_)

        x_list = list()
        # carefully cast x_list/curve dates
        for x in self._curve_.row_keys():
            if BusinessDate.is_businessdate(x):
                x = BusinessDate(x)
            elif BusinessPeriod.is_businessperiod(x):
                x = BusinessPeriod(x).to_businessdate(self.origin)
            else:
                s = repr(x), type(x), BusinessDate.__name__, self.__class__.__name__
                raise ValueError('Cannot cast value %s of type %s to %s in %s construction.' % s)
            x_list.append(x)

        y_list = list(map(float, self._curve_.col('Rate')))
        y_inter = Constant(), self._interpolation_, self._extrapolation_
        if self._rate_type_ == "Zero":
            self._inner_curve = ZeroRateCurve(x_list, y_list, y_inter, self.origin, day_count=self._day_count_)
        else:
            msg = "_curve_ " + self.object_name + ": RateType " + self._rate_type_ + " not implemented, yet."
            raise NotImplementedError(msg)

        self._curve_df_dict = dict()
        return self

    def _day_count(self, start_date, end_date):
        return self._day_count_(start_date, end_date)

    def get_zero_rate(self, start_date, end_date):
        """
        calculates zero rate

        :param BusinessDate end_date:
        :param BusinessDate start_date:
        :return float:
        """

        start_date, end_date = self._cast_to_dates(start_date, end_date)
        zero_rate = self.curve.get_zero_rate(start_date, end_date)
        return zero_rate

    def get_discount_factor(self, start_date, end_date):
        """
        calculates discount factor

        :param BusinessDate start_date: date to discount to
        :param BusinessDate end_date: date to discount from
        :return float: discount factor
        """
        start_date, end_date = self._cast_to_dates(start_date, end_date)
        discount_factor = self.curve.get_discount_factor(start_date, end_date)
        return discount_factor

    def get_cash_rate(self, start_date, end_date=None, tenor_period=BusinessPeriod('1Y')):
        """

        :param start_date:
        :param end_date:
        :param tenor_period:
        :return:
        """
        if end_date is None:
            end_date = start_date + tenor_period
        df = self.get_discount_factor(start_date, end_date)
        t = self._day_count_(start_date, end_date)
        return simple_rate(df, t)
