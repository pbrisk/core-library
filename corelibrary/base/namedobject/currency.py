# coding=utf-8
"""
module containing currency classes
"""

from unicum import FactoryObject


class Currency(FactoryObject):
    """ Currency base class """
    __factory = dict()

    def __init__(self, currency_obj='EUR'):
        super(Currency, self).__init__()
        self._inner_ccy = currency_obj
        self.id = self.__class__.__name__

    def __eq__(self, other):
        return isinstance(other, Currency) and self.id == other.id

    def __str__(self):
        return self.id

    def to_string(self):
        """

        :return:
        """
        return str(self)


# some classes are defined and registered explicitly

class EUR(Currency):
    """ EUR currency class """

    def __init__(self, *args):
        super(EUR, self).__init__('EUR')


class USD(Currency):
    """ USD currency class """

    def __init__(self, *args):
        super(USD, self).__init__('USD')


class GBP(Currency):
    """ GBP currency class """

    def __init__(self, *args):
        super(GBP, self).__init__('GBP')


class CHF(Currency):
    """ CHF currency class """

    def __init__(self, *args):
        super(CHF, self).__init__('CHF')


class JPY(Currency):
    """ JPY currency class """

    def __init__(self, *args):
        super(JPY, self).__init__('JPY')


class SEK(Currency):
    """ SEK currency class """

    def __init__(self, *args):
        super(SEK, self).__init__('SEK')


class TRY(Currency):
    """ TRY currency class """

    def __init__(self, *args):
        super(TRY, self).__init__('TRY')


class PLN(Currency):
    """ PLN currency class """

    def __init__(self, *args):
        super(PLN, self).__init__('PLN')


class RUB(Currency):
    """ RUB currency class """

    def __init__(self, *args):
        super(RUB, self).__init__('RUB')


class AUD(Currency):
    """ AUD currency class """

    def __init__(self, *args):
        super(AUD, self).__init__('AUD')


class CAD(Currency):
    """ CAD currency class """

    def __init__(self, *args):
        super(CAD, self).__init__('CAD')


class CZK(Currency):
    """ CZK currency class """

    def __init__(self, *args):
        super(CZK, self).__init__('CZK')


class DKK(Currency):
    """ DKK currency class """

    def __init__(self, *args):
        super(DKK, self).__init__('DKK')


class HUF(Currency):
    """ HUF currency class """

    def __init__(self, *args):
        super(HUF, self).__init__('HUF')


class MXN(Currency):
    """ MXN currency class """

    def __init__(self, *args):
        super(MXN, self).__init__('MXN')


class NOK(Currency):
    """ NOK currency class """

    def __init__(self, *args):
        super(NOK, self).__init__('NOK')


class ZAR(Currency):
    """ ZAR currency class """

    def __init__(self, *args):
        super(ZAR, self).__init__('ZAR')

class NZD(Currency):
    """ NZD currency class """

    def __init__(self, *args):
        super(NZD, self).__init__('NZD')


EUR().register()
USD().register()
GBP().register()
CHF().register()
JPY().register()
SEK().register()
TRY().register()
PLN().register()
RUB().register()
AUD().register()
CAD().register()
CZK().register()
DKK().register()
HUF().register()
MXN().register()
NOK().register()
ZAR().register()
NZD().register()

