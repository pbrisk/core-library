# coding=utf-8

from putcall import OptionValuatorN, OptionValuatorLN, OptionValuatorSLN

from corelibrary.base.interface.indexmodel import IndexModelInterface, StochasticIndexModelInterface
from corelibrary.base.interface.vol import ImpliedVolInterface
from corelibrary.base.namedobject.optionpayoff import OptionPayoffType


class RealWorldIndexModel(IndexModelInterface):
    """ real world measure index model base class """
    pass


class RiskNeutralIndexModel(IndexModelInterface):
    """ risk neutral measure index model base class """
    pass


class OptionIndexModel(RiskNeutralIndexModel, StochasticIndexModelInterface):
    """ risk neutral measure option pricing index model """

    @property
    def vol(self):
        """ volatility """
        return self._vol_

    def __init__(self, object_name_str=''):
        super(OptionIndexModel, self).__init__(object_name_str)
        self._vol_ = ImpliedVolInterface()
        self._option_pricer = OptionValuatorN()

    def get_option_payoff_value(self, index_object, option_payoff_name, strike_value, reset_date, base_date=None):
        """

        :param index_object:
        :param option_payoff_name:
        :param strike_value:
        :param reset_date:
        :param base_date:
        :return:
        """
        option_type = option_payoff_name
        option_type = option_type if isinstance(option_type, OptionPayoffType) else OptionPayoffType.get(option_type)
        option_type = int(option_type)

        forward_value = self.get_value(index_object, reset_date, base_date)

        start_date = self.vol.origin if base_date is None else base_date  # todo: best fallback is vol.origin?
        time_value = self.vol.day_count(start_date, reset_date)  # todo: better index.day_count?
        vol_value = self.vol.get_volatility(strike_value, start_date, reset_date)

        pricer = self.vol.option_pricer
        option_value = pricer.option_value(forward_value, strike_value, time_value, vol_value, option_type)

        return option_value, vol_value, time_value, forward_value # fixme: return only vol_value


class IntrinsicModel(RealWorldIndexModel, OptionIndexModel):
    """ intrinsic option index model """

    def __init__(self, object_name_str=''):
        super(IntrinsicModel, self).__init__(object_name_str)
        self._inner_model_ = IndexModelInterface

    def get_value(self, index_object, reset_date, base_date=None):
        """

        :param Index index_object:
        :param BusinessDate reset_date:
        :param BusinessDate base_date:
        :return float:
        """
        return index_object.get_value(reset_date, base_date)   # todo: better use _inner_model_.get_value(..)

    def get_option_payoff_value(self, index_object, option_payoff_name, strike_value, reset_date, base_date=None):
        """

        :param index_object:
        :param OptionPayoffType option_payoff_name:
        :param strike_value:
        :param reset_date:
        :param base_date:
        :return:
        """
        option_type = option_payoff_name
        option_type = option_type if isinstance(option_type, OptionPayoffType) else OptionPayoffType.get(option_type)

        fwd_value = self.get_value(index_object, reset_date)
        option_value = option_type.intrinsic_payoff(strike_value, fwd_value)
        return option_value, 0.0, reset_date, fwd_value
