# coding=utf-8


from basederivative import Forward


class Future(Forward):
    """ future product class """
    pass


class MMFuture(Future):
    """ money market future """
    pass


class BondFuture(Future):
    """ bond future """
    pass
