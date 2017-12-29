# coding=utf-8
"""
module for portfolio
"""
from businessdate import BusinessDate

from corelibrary.base.baseobject import ObjectList
from corelibrary.base.interface.pricing import PricingInterface


class Portfolio(PricingInterface):
    """ container for a list of products """

    @property
    def product_list(self):
        """ product list """
        return self._product_list_

    @property
    def domain(self):
        """ all relevant dates """
        d = super(PricingInterface, self).domain
        for p in self._product_list_:
            d.extend(p.domain)
        return sorted(set(d))

    def __init__(self, object_name_str=''):
        super(Portfolio, self).__init__(object_name_str)
        self._product_list_ = ObjectList()

    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns present value at value_date derived by given index_models if provided

        :param value_date:
        :param index_model_dict:
        :return:
        """
        return self._get_present_value_sum(self._product_list_, value_date, index_model_dict)
