from businessdayadjustment import *
from businessholidays import *
from compounding import *
from currency import *
from daycount import *
from frequency import *
from intensitycalulation import *
from interpolation import *
from mapping import *
from masterscaleinterpolation import *
from optionpayoff import *


def create_named_object(name, core_cls, init_object):
    """
        creates a class with the given name

        :param class core_cls:  A class from corelibrary, that is from factorytype and
                                which can be initialized by giving a single object,
                                which is required to meet the needs of the said class

        :param object init_object: init argument

        :return:


        this function creates a class with the given name and the core_cls class as base.
        The init_object is the object required by the base class to be initialised.

    """
    cls = type(name, tuple(core_cls), {"__init__": lambda self: core_cls.__init__(self, init_object)})
    cls.register()


def from_string(string):
    return string


def from_pkg(key, pkgname):
    mod = __import__(pkgname, fromlist=[key])
    obj = getattr(mod, key)
    if type(obj) == type:
        obj = obj()
    return obj



