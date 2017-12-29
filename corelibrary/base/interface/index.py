# coding=utf-8

from businessdate import BusinessDate

from corelibrary.base.baseobject import BusinessObject


class IndexInterface(BusinessObject):
    """ interface class for index objects """

    @property
    def index_model(self):
        """ default IndexModel """
        return self._index_model_

    def get_value(self, reset_date, base_date=None, index_model_dict={}):
        """

        :param Index index_object:
        :param BusinessDate reset_date:
        :param BusinessDate base_date:
        :return float:
        """
        idx_model = index_model_dict.get(self.object_name, self.index_model)
        return idx_model.get_value(self, reset_date, base_date)

    def get_fixing(self, reset_date, value=None):
        """
        depending on whether there exists already a fixing for the index or not
        the saved fixing or the value is returned
        behaves like `dict().get(key, default)`

        :param BusinessDate reset_date: fixing date
        :param float value: default return value, if reset_date fixing not given
        :return float:
        """
        raise NotImplementedError

    def has_fixing(self, reset_date):
        """ check if fixing exists

        :param BusinessDate reset_date:
        :return: bool
        """
        raise NotImplementedError


class RateIndexInterface(IndexInterface):
    """ index interface for rates """
    pass


class SwapRateIndexInterface(IndexInterface):
    """ index interface for swap rates """

    @property
    def discount_index(self):
        """

        :return:
        """
        raise NotImplementedError

    def get_underlying_swap(self, reset_date):
        """ return index underlying swap product """
        raise NotImplementedError
