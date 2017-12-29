# coding=utf-8

from itertools import izip

from businessdate.businessdate import BusinessDate

from corelibrary.base.baseobject import BusinessObject, DataTable, DataRange
from corelibrary.base.namedobject.interpolation import No


class FixingObject(BusinessObject):
    """ base class of objects containing fixings """
    pass


class FixingTable(FixingObject):
    """ contains the fixings for all products which have the index as underlying """

    @property
    def fixing_table(self):
        """ fixing table """
        return self._fixing_table_

    def __init__(self, object_name_str=''):
        super(FixingTable, self).__init__(object_name_str)
        self._location_ = 'London'
        self._time_ = '11:00'
        self._organisation_ = 'ISDA'
        self._ticker_ = 'ISDAFIX2'
        self._fixing_table_ = DataRange([['Date', 'Fixing']])

        self._fixings = None
        self._rebuild_object()

    def _rebuild_object(self):
        dates, values = list(), list()
        if self.fixing_table:
            dates = self.fixing_table.get_column("Date")
            values = self.fixing_table.get_column("Fixing")
        self._fixings = dict(zip(dates, values))
        return self

    def has_fixing(self, reset_date):
        """
        check if fixing exists
        :param BusinessDate reset_date:
        :return: bool
        """
        return reset_date in self._fixings

    def get_fixing(self, reset_date, default_value=None):
        """
        gets fixing if existing else returning default value
        :param BusinessDate reset_date:
        :param float default_value:
        :return: float
        """
        return self._fixings.get(reset_date, default_value)


class MultiFixingTable(FixingObject):
    def __init__(self, object_name_str=''):
        super(MultiFixingTable, self).__init__(object_name_str)
        self._fixing_table_ = DataTable()
        self._fixings = {}
        self._interpolation_ = No()

    def _rebuild_object(self):
        super(MultiFixingTable, self)._rebuild_object()
        if self._is_modified_property('_fixing_table_'):
            dates = [BusinessDate.from_string(str(date)) for date in self._fixing_table_.row_keys()]
            idxs = self._fixing_table_.col_keys()
            date_str_keys = self._fixing_table_.row_keys()
            self._fixings = {}
            for date in dates:
                date_str = str(date)
                # i_date = date_str_keys.index(date_str)
                fixings_per_date = {}
                for idx in idxs:
                    fix = self._fixing_table_.get_item(date_str, idx)
                    fixings_per_date[idx] = fix * 0.01 if fix else None
                self._fixings[date] = fixings_per_date

    def get_fixing(self, date, index_name):
        ret = self._fixings[date][index_name]
        return ret

    def has_fixing(self, date, index_name):
        if date in self._fixings:
            ret = index_name in self._fixings[date]
            return ret
        return False

    def get_fixing_table(self, index):
        def _check_fixing_type(fixing):
            if fixing is None:
                return False
            if isinstance(fixing, str) and fixing.upper() == "NONE":
                return False
            return True

        values = self._fixing_table_.col(index.object_name)
        dates = self._fixing_table_.row_keys()
        tab = [[d, v] for d, v in izip(dates, values) if _check_fixing_type(v)]
        tab.insert(0, ['Date', 'Fixing'])
        fix_tab = DataRange(tab)
        props = ['Currency', 'FixingTable']
        vals = [index.currency, fix_tab]
        ret = FixingTable(index.object_name + "_fixings")
        return ret.modify_object(props, vals)
