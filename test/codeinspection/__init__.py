# coding=utf-8
"""
corelibrary inspection to validate design pattern and coding standards
"""

# this is the improved version of fomerly written Tools
# Jan Dingerkus May 2017 @ Postbank

from excepts import *
from getter import *
from inspectors import *
from logger import Logger, func_to_string
import os
import re


def inspect_attribute(cls, root, attribute_name, log):
    """
    this function inspects whether its interface is according to its root
    interface and spots the difference if there is any. Also it checks if there
    is any public Attribute (meaning a "variable") that is not a property.

    :param class cls:
    :param class root:
    :param str attribute_name:
    :param Logger log:
    """
    if not hasattr(cls, attribute_name):
        raise DeleteAttributeError(attribute_name, cls)

    if not hasattr(root, attribute_name):
        raise MethodNotInRootException(attribute_name, cls)

    cls_method = getattr(cls, attribute_name)
    root_method = getattr(root, attribute_name)

    if not type(cls_method) == type(root_method):
        raise AttributeTypeChangeError(cls, root, attribute_name)

    if not inspect.getargspec(cls_method) == inspect.getargspec(root_method):
        raise SignatureError(cls, root, attribute_name)


def inspect_class(cls, roots, log):
    """
    this function inspects whether its interface is according to its root
    interface and spots the difference if there is any. Also it checks if there
    is any public Attribute (meaning a "variable") that is not a property.

    :param class cls:
    :param class roots:
    :param Logger log:
    """

    def is_visible(attr_name):
        return attr_name.startswith("_") and attr_name.endswith("_") and not is_magic(attr_name)

    my_roots = [r for r in roots if issubclass(cls, r)]
    my_roots_methods = list()
    for r in my_roots:
        my_roots_methods.extend(get_public_method_names(r))
    my_roots_properties = list()
    for r in my_roots:
        my_roots_properties.extend(get_public_property_names(r))

    for root in my_roots:
        # 1 checking if it has given root (otherwise not interesting)

        if not root in inspect.getmro(cls):
            return

        # 2 get all overwritten or new methods or properties

        overwritten_method_names = get_overwritten_attr_names(cls, root, get_method_names)
        new_method_names = get_new_attr_names(cls, root, get_method_names)
        new_method_names = [n for n in new_method_names if not n.startswith('_')]

        overwritten_static_method_names = get_overwritten_attr_names(cls, root, get_static_methods)
        new_static_method_names = get_new_attr_names(cls, root, get_static_method_names)
        new_static_method_names = [n for n in new_static_method_names if not n.startswith('_')]

        overwritten_property_names = get_overwritten_attr_names(cls, root, get_property_names)
        new_property_names = get_new_attr_names(cls, root, get_property_names)
        new_property_names = [n for n in new_property_names if not n.startswith('_')]

        # 3 additional attributes only occurring in an instance

        try:
            difference_cls = get_attributes_difference_names(cls)
            difference_root = get_attributes_difference_names(root)
            difference = [name for name in difference_cls if name not in difference_root]

        except EmptyInitializationError as e:
            log.err(e)
        else:
            for name in difference:
                msg = "ATTRIBUTE".ljust(12) + str(cls) + "." + name
                if is_public(name):
                    log_attr_name = str(cls) + "." + name
                    log.err(IsPublicError(log_attr_name))
                elif is_private(name):
                    msg += "...is private. "
                    name = name.strip("_")
                    try:
                        is_property(cls, name)
                    except AttributeError:
                        pass
                    else:
                        msg += 'There is a property named "' + name + '"'
                    log(msg)
                elif is_visible(name):
                    msg += "...is visible. "
                    name = name.lstrip("_").rstrip("_")
                    try:
                        is_property(cls, name)
                    except AttributeError:
                        pass
                    else:
                        msg += 'There is a property named "' + name + '"'
                    log(msg)

        # 4 validate signatures

        def assert_signature(cls, root, method_name):
            cls_method = getattr(cls, method_name)
            root_method = getattr(root, method_name)

            cls_argsinsprect = getargsinspect(cls_method)
            root_argsinspect = getargsinspect(root_method)

            if not cls_argsinsprect == root_argsinspect:
                raise SignatureError(cls, root, method_name)

        for method_name in overwritten_method_names + overwritten_static_method_names:
            try:
                assert_signature(cls, root, method_name)
            except SignatureError as e:
                log.err(e)

        # 5 validate new methods and properties

        for property_name in new_property_names:
            if property_name not in my_roots_properties:
                property_string = cls.__name__ + "." + property_name
                log.err(PropertyNotInRootException(property_string, my_roots))

        for method_name in new_method_names + new_static_method_names:
            if method_name not in my_roots_methods:
                method = getattr(cls, method_name)
                func_string = func_to_string(method, cls)
                log.err(MethodNotInRootException(func_string, my_roots))


def inspect_classes(classes, roots, log):
    """
    this function inspects whether its interface is according to its root
    interface and spots the difference if there is any. Also it checks if there
    is any public Attribute (meaning a "variable") that is not a property.

    :param list(cls) classes:
    :param list(cls) roots:
    :param Logger log:
    """
    for cls in classes:
        log("INSPECTING".ljust(12) + str(cls))
        inspect_class(cls, roots, log)
    log.log_errors()


def inspect_imports(path, log):
    import_lines = list()
    for d, s, fl in os.walk(path):
        for filename in fl:
            if filename.endswith('py'):
                filepath = os.path.join(d, filename)
                with open(filepath) as f:
                    for i, line in enumerate(f):
                        if line.find("import") != -1:
                            import_lines.append((filepath, i, line.strip()))

    def split(filename):
        return filename.split(os.sep)

    for filename, linenumber, line in import_lines:

        s = split(filename)
        if line.find("*") != -1 and not filename.endswith('__init__.py'):
            log.err(WildCardImportException(filename, linenumber, line))
        elif re.search('[ .]analytics[ .]', line) and ("business" in s):
            log.err(WrongPlaceImportException(filename, linenumber, line))
        elif re.search('[ .]business[ .]', line) and "analytics" in s:
            log.err(WrongPlaceImportException(filename, linenumber, line))


def inspect_module(module_name, log, base_class_name='object', is_root=None):
    """
    this function inspects whether its interface is according to its root
    interface and spots the difference if there is any. Also it checks if there
    is any public Attribute (meaning a "variable") that is not a property.

    :param cls:
    :param Logger log:
    :param str base_class_name:
    """

    try:
        mod = __import__(module_name)
    except ImportError as e:
        log.err(e)
        log.log_errors()
    else:
        path = os.path.split(mod.__file__)[0]
        inspect_imports(path, log)
        base_class = getattr(mod, base_class_name)
        if is_root is None:
            roots = [cls for cls in get_classes(mod) if issubclass(cls, base_class) and cls != base_class]
        else:
            roots = [cls for cls in get_classes(mod) if issubclass(cls, base_class) and is_root(cls)]
        classes = [cls for cls in get_classes(mod) if issubclass(cls, base_class)]
        inspect_classes(classes, roots, log)


if __name__ == "__main__":
    # ignore_list = [NoRootException, MethodNotInRootException, PropertyNotInRootException, SignatureError]
    # log = Logger("codeinspection.log", stout=True, fileout=False)

    ignore_list = [PropertyNotInRootException]
    log = Logger("codeinspection.log", ignore_list=ignore_list, stout=True, fileout=False, level='ERROR')
    inspect_module("corelibrary", log, base_class_name="VisibleObject", is_root=lambda c: c.__name__.endswith('Interface'))
