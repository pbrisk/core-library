# coding=utf-8
"""
defining index
"""

from corelibrary.base.interface.indexmodel import IndexModelInterface
from corelibrary.base.interface.defaultcurve import DefaultProbabilityInterface


class CreditIndexModel(IndexModelInterface):
    """ base credit index """

    def __init__(self, object_name_str=''):
        super(CreditIndexModel, self).__init__(object_name_str)
        self._default_probability_ = DefaultProbabilityInterface()


class SurvivalIndexModel(CreditIndexModel):
    """ index providing survival probabilities """

    def get_value(self, index_object, reset_date, base_date=None):
        """
        returns the cumulative survival probability of the underlying curve

        :param index_object:
        :param reset_date:
        :param base_date:
        :return:
        """
        end_date = index_object._rolling_method_.adjust(reset_date)
        return self._default_probability_.get_survival_probability(index_object._pd_, end_date, index_object._origin_)
