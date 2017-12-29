# coding=utf-8
"""
fx index model
"""

from putcall.optionvaluator import OptionValuatorLN

from corelibrary.base.interface.fxcurve import FxCurveInterface
from corelibrary.base.interface.vol import VolInterface

from baseindexmodel import OptionIndexModel


class FXIndexModel(OptionIndexModel):
    """ IndexModel for FXIndex """

    def __init__(self, object_name_str=''):
        super(FXIndexModel, self).__init__(object_name_str)
        self._vol_ = VolInterface()
        self._fx_curve_ = FxCurveInterface()
        self._option_pricer = OptionValuatorLN()

    def get_value(self, index_object, reset_date, base_date=None):
        """

        :param index_object:
        :param reset_date:
        :param base_date:
        :return:
        """
        assert base_date is None, "base_date has to be None by FXIndex.get_forward"
        return self._fx_curve_.get_value(reset_date)
