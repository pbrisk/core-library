# coding=utf-8
"""
defining index
"""

from corelibrary.analytics.model.indexmodel import CreditIndexModel

from corelibrary.base.namedobject import TAR, ModFollow

from baseindex import Index


class CreditIndex(Index):
    """ base credit index """
    pass


class SurvivalIndex(CreditIndex):
    """ index providing survival probabilities """

    def __init__(self, object_name_str=''):
        super(SurvivalIndex, self).__init__(object_name_str)
        self._index_model_ = CreditIndexModel()
        self._calendar_ = TAR()
        self._rolling_method_ = ModFollow()  # todo add CDS_IMM to rolling method
        self._rolling_method_.holidays = self._calendar_
        self._pd_ = 0.001
