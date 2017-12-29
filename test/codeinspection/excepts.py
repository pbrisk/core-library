# coding=utf-8
"""
code inspection exceptions
"""

from logger import func_to_string


class BaseError(Exception):
    """
    Base class for errors
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.__class__.__name__ + " : " + self.msg


class EmptyInitializationError(BaseError):
    """
    If an instance of class can't be created without any arguments this
    error is risen.
    """

    def __init__(self, cls):
        super(EmptyInitializationError, self).__init__(
            "Instance of {} couldn't be initialized without arguments".format(cls))


class DeleteAttributeError(BaseError):
    """
    If an attribute was deleted, this error is risen.
    """

    def __init__(self, func_string, cls):
        super(DeleteAttributeError, self).__init__(func_string + " was deleted {}".format(cls))


class AttributeTypeChangeError(BaseError):
    """
    If type of attribute changed, this error is risen.
    """
    def __init__(self, cls, root, attribute_name):
        msg = attribute_name, cls.__name__, root.__name__
        super(AttributeTypeChangeError, self).__init__('attribute %s change type in %s since root %s' %msg)


class NoRootException(BaseError):
    """
    If a class has no root class to which it could be compared this
    error is risen.
    """

    def __init__(self, obj):
        super(NoRootException, self).__init__("No root found for {}".format(obj))


class MethodNotInRootException(BaseError):
    """
    If a new method was defined, that was not already defined in the
    root class, this error is risen.
    """

    def __init__(self, func_string, root_cls):
        if isinstance(root_cls, (list, tuple)):
            root_cls = ' nor '.join(str(c.__name__) for c in root_cls)
        msg = func_string + "\n            was not defined in root    {}".format(str(root_cls))
        super(MethodNotInRootException, self).__init__(msg)


class PropertyNotInRootException(MethodNotInRootException):
    """
    If a new porperty was defined, that was not already defined in the
    root class, this error is risen.
    """
    pass


class IsPublicError(BaseError):
    """
    If an attribute of an object is public, when it actually shouldn't
    be, this error is risen.
    """

    def __init__(self, log_attr_name):
        super(IsPublicError, self).__init__(log_attr_name + "...shouldn't be Public")


class SignatureError(BaseError):
    """
    If an overwritten method does not share the interface with the
    method defined in the root class this error is risen
    """

    def __init__(self, cls, root, method_name):
        cls_method = getattr(cls, method_name)
        root_method = getattr(root, method_name)

        func_string = func_to_string(cls_method, cls)
        reference_func_string = func_to_string(root_method, root)

        o1, m1 = func_string.split('.', 1)
        o2, m2 = reference_func_string.split('.', 1)
        l = max(len(o1), len(o2)) + 1
        o1 = (' ' + o1).rjust(l, '_')
        o2 = (' ' + o2).rjust(l, '_')

        msg = "%s.%s" % (o1, m1) + "\n"
        msg += "            disagrees with   "
        msg += "%s.%s" % (o2, m2)
        super(SignatureError, self).__init__(msg)

class WildCardImportException(BaseError):
    """
    Wildcard imports should not appear in the source code.
    """
    def __init__(self, filename, linenumber, line):
        msg = "WildCardImport in {name}\n                 in line {number} : {content} ".format(name=filename,
                                                                                           number=linenumber,
                                                                                           content=line)
        super(WildCardImportException, self).__init__(msg)

class WrongPlaceImportException(BaseError):
    """
    If an element from wrong place in hierachy of packages is imported.
    """
    def __init__(self, filename, linenumber, line):
        msg = "WrongPlaceImport in {name}\n                 in Line {number} : {content} ".format(name=filename,
                                                                                             number=linenumber,
                                                                                             content=line)
        super(WrongPlaceImportException, self).__init__(msg)
