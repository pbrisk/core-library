# coding=utf-8
""" defining CrossCurrencySwaps """

from corelibrary.base.interface.index import IndexInterface
from irswap import CashFlowListIRSwap


class CcySwap(CashFlowListIRSwap):
    """ cross currency swap """
    def __init__(self, object_name_str=''):
        super(CcySwap, self).__init__(object_name_str)
        self._f_x_index_ = IndexInterface()
