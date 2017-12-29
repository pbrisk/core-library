# coding=utf-8
"""
getter functions
"""

import inspect
import types
from inspectors import is_public, is_private, is_magic, is_property, is_static_method, is_method, is_overwritten


def get_classes(module):
    return [getattr(module, name) for name in dir(module) if inspect.isclass(getattr(module, name))]


def get_attributes_difference(cls):
    obj = cls()
    class_attributes = get_attribute_names(cls)
    instance_attributes = get_attribute_names(obj)
    for a in class_attributes:
        instance_attributes.remove(a)

    return [getattr(obj, name) for name in instance_attributes]


def get_attributes(obj):
    return [getattr(obj, name) for name in sorted(dir(obj))]


def get_public_attributes(obj):
    return [attr for attr in get_attributes(obj) if is_public(attr.__name__)]


def get_private_attributes(obj):
    return [attr for attr in get_attributes(obj) if is_private(attr.__name__)]


def get_magic_attributes(obj):
    return [attr for attr in get_attributes(obj) if is_magic(attr.__name__)]


def get_properties(obj):
    return [attr for attr in get_attributes(obj) if isinstance(attr, property)]


def get_property_getters(obj):
    return [prop.fget for prop in get_properties(obj)]


def get_public_properties(obj):
    return [attr for attr in get_properties(obj) if is_public(attr.__name__)]


def get_private_properties(obj):
    return [attr for attr in get_properties(obj) if is_private(attr.__name__)]


def get_static_methods(obj):
    return [attr for attr in get_attributes(obj) if isinstance(attr, types.FunctionType)]


def get_public_static_methods(obj):
    return [attr for attr in get_static_methods(obj) if is_public(attr.__name__)]


def get_private_static_methods(obj):
    return [attr for attr in get_static_method_names(obj) if is_private(attr.__name__)]


def get_methods(obj):
    return [attr for attr in get_attributes(obj) if isinstance(attr, types.MethodType)]


def get_public_methods(obj):
    return [attr for attr in get_methods(obj) if is_public(attr.__name__)]


def get_private_methods(obj):
    return [attr for attr in get_methods(obj) if is_private(attr.__name__)]


# NAME GETTERS ----------------------------------------------------------------

def get_attribute_names(obj):
    return dir(obj)


def get_attributes_difference_names(cls):
    obj = cls()
    class_attributes = get_attribute_names(cls)
    instance_attributes = get_attribute_names(obj)
    for a in class_attributes:
        instance_attributes.remove(a)
    return instance_attributes


def get_public_attribute_names(obj):
    return sorted([attr for attr in dir(obj) if is_public(attr)])


def get_private_attribute_names(obj):
    return sorted([attr for attr in dir(obj) if not is_private(attr)])


def get_magic_attribute_names(obj):
    return sorted([attr for attr in dir(obj) if not is_magic(attr)])


def get_property_names(obj):
    return sorted([attr for attr in get_attribute_names(obj) if is_property(obj, attr)])


def get_public_property_names(obj):
    return sorted([attr for attr in get_public_attribute_names(obj) if is_property(obj, attr)])


def get_private_property_names(obj):
    return sorted([attr for attr in get_private_attribute_names(obj) if is_property(obj, attr)])


def get_static_method_names(obj):
    return sorted([attr for attr in get_attribute_names(obj) if is_static_method(obj, attr)])


def get_public_static_method_names(obj):
    return sorted([attr for attr in get_public_attribute_names(obj) if is_static_method(obj, attr)])


def get_private_static_method_names(obj):
    return sorted([attr for attr in get_private_attribute_names(obj) if is_static_method(obj, attr)])


def get_method_names(obj):
    return sorted([attr for attr in get_attribute_names(obj) if is_method(obj, attr)])


def get_public_method_names(obj):
    return sorted([attr for attr in get_public_attribute_names(obj) if is_method(obj, attr)])


def get_private_method_names(obj):
    return sorted([attr for attr in get_private_attribute_names(obj) if is_method(obj, attr)])


def get_overwritten_attr_names(cls, base_cls, attr_name_getter):
    """
    Returns a list of list of overwritten attributes of cls compared to base_

    :param class cls: A class
    :param class base_cls: Any base class form cls
    :param attr_getter:
    :return:
    """
    base_cls_attr_names = attr_name_getter(base_cls)
    res = list()
    for attr_name in base_cls_attr_names:
        base_cls_attr = getattr(base_cls, attr_name)
        cls_attr = getattr(cls, attr_name)

        overwritten = False

        if isinstance(cls_attr, types.MethodType):
            overwritten = is_overwritten(cls_attr, base_cls_attr)
        elif isinstance(cls_attr, property):
            if hasattr(cls_attr, 'fget') and hasattr(base_cls_attr, 'fget'):
                overwritten = is_overwritten(cls_attr.fget, base_cls_attr.fget)
            else:
                print 'ignore ' + attr_name + ' at ' + str(cls)
                #overwritten = is_overwritten(cls_attr, base_cls_attr)

        if overwritten:
            res.append(attr_name)

    return res


def get_new_attr_names(cls, base_cls, attr_name_getter):
    """
    Returns a list of attribute names that have been defined on top those already defined in base_cls

    :param cls:
    :param base_cls:
    :param attr_name_getter:
    :return:
    """

    attr_names = attr_name_getter(cls)
    base_cls_attr_names = attr_name_getter(base_cls)

    return [name for name in attr_names if name not in base_cls_attr_names]


def getargsinspect(method):
    if hasattr(method, 'getargsinspect'):
        # maybe root_method is actually defined in decorator
        return method.getargsinspect
    else:
        return inspect.getargspec(method)
