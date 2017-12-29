# coding=utf-8

from businessdate import BusinessDate, BusinessPeriod

from corelibrary.base.baseobject import ObjectList
from corelibrary.base.interface.pricing import PricingInterface
from corelibrary.business.index import CreditIndex, FXIndex
from corelibrary.business.party import Party


class Contract(PricingInterface):
    """ Contract """

    @property
    def effective_rate(self):
        """ aka yield to maturity """
        return self._effective_rate_

    def __init__(self, object_name_str=''):
        super(Contract, self).__init__(object_name_str)
        self._f_x_index_ = FXIndex()
        self._party_ = Party()
        self._product_list_ = ObjectList()

        self._approved_amount_ = 0.
        self._effective_rate_ = 0.

        self._credit_index_ = CreditIndex()

    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ gets the present value of a contract

        Parameters:
            value_date (BusinessDate): the value date of the contract
            index_model_dict (dict): dict of IndexModels

        Returns:
            float: present value for given value_date
        """

        sum_pv = self.get_present_value_sum(self._product_list_, value_date, index_model_dict)
        return sum_pv

    def get_positive_exposure(self, value_date=BusinessDate(), index_model_dict={}):
        """ gets the positive exposure of a contract

        Parameters:
            value_date (BusinessDate): the value date of the contract
            index_model_dict (dict): dict of IndexModels

        Returns:
            float: positive exposure for given value_date

        """
        sum_positive_exposure = 0.0
        for prod in self._product_list_:
            sum_positive_exposure += prod.get_positive_exposure(value_date)[0]

        return sum_positive_exposure
