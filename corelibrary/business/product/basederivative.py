# coding=utf-8

from businessdate.businessdate import BusinessDate
from mitschreiben import Record

from corelibrary.base.interface.pricing import PricingInterface
from corelibrary.base.namedobject.businessholidays import Calendar
from corelibrary.base.namedobject.optionpayoff import OptionPayoffType

from baseproduct import Product

class DerivativeProduct(Product):
    """ derivative base class """
    pass


class Forward(DerivativeProduct):
    """ forward product base class """
    pass


class SwapProduct(DerivativeProduct):
    """ swap product base class """

    @property
    def leg_list(self):
        """ list of legs """
        raise NotImplementedError

    @property
    def discount_index(self):
        """ DiscountIndex """
        return self._discount_index_

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns present value at value_date derived by given index_models if provided

        :param value_date:
        :param index_model_dict:
        :return: float, the pv of the cash flow
        """

        return self._get_present_value_sum(self.leg_list, value_date, index_model_dict)


class Option(DerivativeProduct):
    """ option base class """

    @property
    def option_type(self):
        """ type of option (call or put) """
        return self._option_type_

    def __init__(self, object_name_str=''):
        super(Option, self).__init__(object_name_str)
        self._option_payoff_type_ = OptionPayoffType()
        self._exercise_date_ = BusinessDate()
        self._settlement_date_ = BusinessDate()
        self._calendar_ = Calendar()
        self._option_position_ = "Long"  # todo: make OptionPosition a namedobject

    def _rebuild_object(self):
        super(Option, self)._rebuild_object()
        if not '_settlement_date_' in self._modified_members:
            self._settlement_date_ = self._exercise_date_
        return self
