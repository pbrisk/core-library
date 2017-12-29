# coding=utf-8

from corelibrary.base.interface.fxcurve import FxCurveInterface
from corelibrary.base.interface.yieldcurve import YieldCurveInterface
from corelibrary.base.namedobject.businessholidays import TAR

from spot import FxSpot


class FxCurve(FxCurveInterface):
    """ _fx_curve_ object """
    def __init__(self, object_name_str=''):
        super(FxCurve, self).__init__(object_name_str)
        self._calendar_ = TAR()
        self._b_days_to_settle_ = 2  # fixme do better
        self._spot_ = FxSpot(1.0)
        self._dom_curr_curve_ = YieldCurveInterface()
        self._for_curr_curve_ = YieldCurveInterface()

    def get_value(self, reset_date):
        """
        :param reset_date:
        :param base_date:
        :return float:
        """
        settle_date = self._origin_.add_business_days(self._b_days_to_settle_, self._calendar_)
        reset_modified = reset_date.add_business_days(self._b_days_to_settle_, self._calendar_)
        df_foreign = self._for_curr_curve_.get_discount_factor(settle_date, reset_modified)
        df_domestic = self._dom_curr_curve_.get_discount_factor(settle_date, reset_modified)
        ret = self._spot_ * df_foreign / df_domestic
        return ret