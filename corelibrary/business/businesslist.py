# coding=utf-8

from corelibrary.base import VisibleList
import index
from index import Index


class IndexList(VisibleList):
    """ IndexList class """

    def __init__(self, object_name_str=''):
        self._list_type = Index
        self._list_module = index
        super(IndexList, self).__init__(object_name_str)
