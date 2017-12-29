# coding=utf-8
"""
module containing currency classes
"""

from unicum import FactoryObject
from putcall.optionvaluator import OptionType as _OptionType


class OptionPayoffType(FactoryObject):
    """ option payoff base class """
    __factory = dict()

    def intrinsic_payoff(self, strike_value, underlying_value):
        """

        :param strike_value:
        :param underlying_value:
        :return:
        """
        raise NotImplementedError

    def __int__(self):
        raise NotImplementedError


# some classes are defined and registered explicitly

class Call(OptionPayoffType):
    """ call option payoff """

    def intrinsic_payoff(self, strike_value, underlying_value):
        """

        :param strike_value:
        :param underlying_value:
        :return:
        """
        return max(0., underlying_value - strike_value)

    def __int__(self):
        return _OptionType.CALL


class Put(OptionPayoffType):
    """ put option payoff """

    def intrinsic_payoff(self, strike_value, underlying_value):
        """

        :param strike_value:
        :param underlying_value:
        :return:
        """
        return max(0., strike_value - underlying_value)

    def __int__(self):
        return _OptionType.PUT


Call().register()
Call().register('CALL', 'call')
Put().register()
Put().register('PUT', 'put')
