import dcf
from unicum import FactoryObject


class Interpolation(FactoryObject):
    """ base interpolation class """
    __factory = dict()

    def __init__(self, *args):
        super(Interpolation, self).__init__()


class Constant(dcf.constant, Interpolation):
    """ constant interpolation """
    pass


class Linear(dcf.linear, Interpolation):
    """ linear interpolation """
    pass


class No(dcf.no, Interpolation):
    """ no interpolation """
    pass


class Zero(dcf.zero, Interpolation):
    """ zero interpolation """
    pass


# register instances

Constant().register()
Constant().register('CONSTANTZERO', 'CONSTANT')

Linear().register()
Linear().register('LINEARZERO', 'LINEAR')

No().register()
No().register('NO', 'NoInterpolation')

Zero().register()
Zero().register('ZERO', 'ZeroInterpolation')
