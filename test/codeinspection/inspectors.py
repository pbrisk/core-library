# coding=utf-8
"""
inspector functions for attributes
"""

import types


def is_public(attr_name):
    return not attr_name.startswith("_")


def is_private(attr_name):
    return attr_name.startswith("_") and not attr_name.endswith("_")


def is_magic(attr_name):
    return attr_name.startswith("__") and attr_name.endswith("__")


def is_overwritten(child_method, ancestor_method):
    return child_method.func_code != ancestor_method.func_code


def is_property(obj, attr_name):
    attr = getattr(obj, attr_name)
    return isinstance(attr, property)


def is_method(obj, attr_name):
    attr = getattr(obj, attr_name)
    return isinstance(attr, types.MethodType)


def is_static_method(obj, attr_name):
    attr = getattr(obj, attr_name)
    return isinstance(attr, types.FunctionType)



