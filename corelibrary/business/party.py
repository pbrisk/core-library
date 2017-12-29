# coding=utf-8

from corelibrary.base.baseobject import BusinessObject
from corelibrary.business.index import SurvivalIndex


class Party(BusinessObject):
    """ basic counterparty class """

    @property
    def survival_index(self):
        """ index providing survival probabilities """
        return self._survival_index_

    def __init__(self, object_name_str=''):
        super(Party, self).__init__(object_name_str)
        self._rating_ = 'NotRated'  # todo make rating class master_scale property or NamedObject
        self._credit_index_ = SurvivalIndex()
