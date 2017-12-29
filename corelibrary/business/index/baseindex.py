# coding=utf-8
"""
defining index
"""

from dcf import DateCurve, no, linear

from corelibrary.base.baseobject import BusinessObject
from corelibrary.base.interface.index import IndexInterface
from corelibrary.base.interface.indexmodel import IndexModelInterface
from corelibrary.business.fixing import FixingTable, MultiFixingTable


class Index(IndexInterface):
    """ base index class """

    @property
    def fixing_table(self):
        """ fixing table: storage for fixings """
        return self._fixing_table_

    def __init__(self, object_name_str=''):
        super(Index, self).__init__(object_name_str)
        self._index_model_ = IndexModelInterface()
        self._fixing_table_ = FixingTable()
        self._multi_fixing_table_ = MultiFixingTable()

        self._scenario_fixings = None

    def has_fixing(self, reset_date):
        """ check if fixing exists

        :param BusinessDate reset_date:
        :return: bool
        """
        if self.fixing_table.has_fixing(reset_date) or self._multi_fixing_table_.has_fixing(reset_date, self.object_name):
            return True
        elif self._scenario_fixings:
            dom = self._scenario_fixings.domain
            return dom[0] <= reset_date <= dom[-1]

    def get_fixing(self, reset_date, value=None):
        """
        depending on whether there exists already a fixing for the index or not
        the saved fixing or the value is returned
        behaves like `dict().get(key, default)`

        :param BusinessDate reset_date: fixing date
        :param float value: default return value, if reset_date fixing not given
        :return float:
        """
        if self.has_fixing(reset_date):
            if self.fixing_table.has_fixing(reset_date):
                return self.fixing_table.get_fixing(reset_date)
            elif self._multi_fixing_table_.has_fixing(reset_date, self.object_name):
                return self._multi_fixing_table_.get_fixing(reset_date, self.object_name)
            else:
                return self._scenario_fixings(reset_date)
        else:
            return value

    # --- deprecated methods ---

    def get_value(self, reset_date, base_date=None, index_model_dict={}):
        # todo: remove IndexModel methods (get_value) from Index ?
        return self._index_model_.get_value(self, reset_date, base_date)

    def _modify_property(self, property_name, property_value_variant):
        # todo: workaround to run legacy configurations when Index had IndexModel properties
        if not self._index_model_.is_modified:
            self._index_model_ = self._index_model_.__class__(self.object_name + '-IndexModel')
        if hasattr(self._index_model_, property_name):
            self._index_model_._modify_property(property_name, property_value_variant)
        if hasattr(self, property_name):
            super(Index, self)._modify_property(property_name, property_value_variant)
