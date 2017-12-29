# coding=utf-8

from businessdate import BusinessDate
from mitschreiben import Record

from corelibrary.base.baseobject import DataRange
from corelibrary.base.interface.pricing import PricingInterface
from corelibrary.business.index import FXIndex, DiscountIndex


class Product(PricingInterface):
    """ basic Product class """

    @property
    def discount_index(self):
        """ DiscountIndex """
        return self._discount_index_

    @property
    def notional(self):
        """ notional """
        return self._notional_

    def __init__(self, object_name_str=''):
        super(Product, self).__init__(object_name_str)
        self._f_x_index_ = FXIndex()
        self._discount_index_ = DiscountIndex()
        self._notional_ = 1000000.00
        self._price_ = 0.0
        self._trade_i_d_ = -1

    def get_positive_exposure(self, value_date=BusinessDate(), index_model_dict={}):
        """

        :param value_date:
        :param index_model_dict: container of IndexModels
        :type index_model_dict: dict
        :return:
        """
        pay_value = self.get_present_value(value_date, index_model_dict)
        return max(pay_value, 0)


class Payment(Product):
    """ single Payment """

    def __init__(self, object_name_str=''):
        super(Payment, self).__init__(object_name_str)
        self._pay_date_ = BusinessDate.add_period(self.origin, '3M')

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """

        :param value_date:
        :param index_model_dict:
        :return:
        """
        pv_let = 0.0
        pv_let_value_ccy = None
        df = None
        fx = None

        if self._pay_date_ > value_date:
            fx = 1.0  # fixme: handle other ccy, too.
            df = self._discount_index_.get_value(self._pay_date_, value_date)
            pv_let_value_ccy = df * self._notional_
            pv_let = fx * pv_let_value_ccy

        Record(notional=self._notional_,
               pay_date=self._pay_date_,
               disc_fact=df,
               fx=fx,
               pv_let=pv_let,
               pv_let_value_ccy=pv_let_value_ccy,
               disc_index=self._discount_index_.object_name,
               fx_index=self._f_x_index_.object_name)

        return pv_let
