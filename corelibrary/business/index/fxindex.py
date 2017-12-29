# coding=utf-8
"""
defining index
"""

from corelibrary.analytics.model.indexmodel import FXIndexModel

from corelibrary.base.interface.fxcurve import FxCurveInterface
from corelibrary.base.interface.vol import VolInterface
from corelibrary.base.namedobject import Currency
from baseindex import Index


class FXIndex(Index):
    """ contains discount curves adjusted by cross-currency basis, e.g. for the calculation of exchange rates """

    @property
    def domestic_currency(self):
        """ domestic currency """
        return self._index_model_._fx_curve_._dom_curr_curve_.currency  # todo: use own currency

    @property
    def foreign_currency(self):
        """ foreign currency """
        return self._index_model_._fx_curve_._for_curr_curve_.currency  # todo: use own currency

    def __init__(self, object_name_str=''):
        super(FXIndex, self).__init__(object_name_str)
        self._index_model_ = FXIndexModel()
        self._domestic_currency_ = Currency()
        self._foreign_currency_ = Currency()


class FXValueInv(object):  # fixme: InverseFXIndex should be FXIndex
    """The inverse Value of an FX Index"""

    @property
    def domestic_currency(self):
        """ domestic currency """
        return self._fx_index.foreign_currency

    @property
    def foreign_currency(self):
        """ foreign currency """
        return self._fx_index.domestic_currency

    def __init__(self, fx_index):
        self._fx_index = fx_index

    def get_value(self, reset_date, base_date=None, index_model_dict={}):
        """

        :param reset_date:
        :param base_date:
        :return:
        """
        return 1.0 / self._fx_index.get_value(reset_date, base_date)  # todo: use index_model

    def __str__(self):
        return "Inverse_of_" + self._fx_index.object_name