# coding=utf-8
""" main init module """

import os
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import RotatingFileHandler

from analytics import *
from base import *
from business import *
from utils import *

# --- config ---
version = '0.1 dev'
status = 'initial development'
release_date = date(2017, 12, 31)
contact = 'pbrisk_at_github@icould.com'


# --- logger ---
def init_logger(log_name='corelibrary', log_path=None, log_level=10, stdout_level=30, file_level=10):
    """inits logger"""

    _short_format = '%(asctime)s %(levelname)-5s %(message)s'
    _long_format = '%(asctime)s %(module)-14s %(levelname)-8s %(message)-120s'

    if log_path is None:
        log_path = os.getcwd() + os.path.sep + 'pace.log'
    elif os.path.isdir(log_path):
        log_path += os.path.sep + 'pace.log'

    core_logger = getLogger(log_name)

    if stdout_level is not None:
        stdout_handler = StreamHandler()
        stdout_handler.setFormatter(Formatter(_short_format, '%Y%m%d %H%M%S'))
        stdout_handler.setLevel(stdout_level)
        core_logger.addHandler(stdout_handler)

    if file_level is not None:
        file_handler = RotatingFileHandler(log_path, backupCount=10)
        file_handler.doRollover()
        file_handler.setFormatter(Formatter(_long_format, '%Y-%m-%d %H:%M:%S'))
        file_handler.setLevel(file_level)
        core_logger.addHandler(file_handler)

    core_logger.setLevel(log_level)
    return core_logger


# --- start ---
core_log = init_logger('corelibrary', log_level=100, file_level=None)
core_log.info('')
core_log.info('***********************************************')
core_log.info('')
core_log.info('  welcome to corelibrary %s, %s' % (version, release_date.strftime('%Y-%m-%d')))
core_log.info('     A core financial risk analytics library.')
core_log.info('')
core_log.debug('  %s version' % status)
core_log.debug('  please register your application at')
core_log.debug('     %s' % contact)
core_log.debug('')
core_log.info('***********************************************')
core_log.info('')


# --- loading generic/custom data ---
def find_file(filepath):
    root = __file__.split("pace")[0]
    root = os.path.join(root, "pace")
    part_of_path, filename = os.path.split(filepath)
    for d, s, f in os.walk(root):
        if filename in f and d.endswith(part_of_path):
            return os.path.normpath(os.path.join(d, filename))
    part_of_path, filename = os.path.split(__file__)
    return part_of_path + os.sep + '..' + os.sep + filepath


# Getting UserConfiguration as dict from file via json
with open(find_file("core_config.json")) as config_file:
    config_dict = json.load(config_file)

# [NAMED_OBJECTS]
# in the following the NAMED_OBJECT entry in the config_dict is used to create and register named_objects
# The entry is a list of dicts with up to 6 keys
keys = ["class", "keys", "load_function", "load_function_file", "load_args", "aliases"]
# class:      a string specifying a named_object class from corelibrary
# keys:       a list of strings which are the names under that the new created classes are registered and that are used
#             to obtain objects to initialize instances of those new created classes
# load_function: a string naming a function that is used to obtain an obj from a key, with that a class instance
#             is initialized.
# load_function_file: a string naming a python file in which a load_function is defined. The interface should be of
#             the form func(key, *args)
# load_args: is a list of strings that can be processed by the load_function, when passing it as *args
# aliases:    a dict containing a list of aliasnames (strings) for any key in keys.
#             once a named object is created  under the key as name it is registered with this class/key name.
#             To reference this object with
#             a different name the aliases are registered

extended_items = [[obj.get(key, '') for key in keys] for obj in config_dict["NAMED_OBJECTS"]]

for cls, keys, func, func_file, args, aliases in extended_items:
    cls = locals()[cls]
    if func_file:
        func_file = find_file(func_file)
        execfile(func_file)
    func = locals()[func]
    keys = [key.encode("ASCII") for key in keys]
    for key in keys:
        obj = func(key, *args)
        new_cls = type(key, (cls,), {"__init__": lambda self: cls.__init__(self, obj)})().register()
    if aliases:
        for key in keys:
            cls(key).register(*aliases[key])

# [GENERIC_OBJECTS]
for filename in config_dict["GENERIC_OBJECTS"]:
    filename = find_file(filename)
    res = VisibleObject.load_objects_from_file(filename)
    for obj in res:
        obj.make_generic()

# with open(os.getcwd() + os.sep + "core_config.json") as config_file:
#     config_dict = json.load(config_file)
# load_items = ["class", "keys", "load_function", "load_function_file", "load_args", "aliases"]
# extended_items = [[obj.get(item, '') for item in load_items] for obj in config_dict["Objects"]]
#
# for cls, keys, func, func_file, args, aliases in extended_items:
#     cls = getattr(corelibrary, cls.encode("ASCII"))
#     if func_file:
#         # read load function from func_file
#         func_file = os.getcwd() + os.sep + func_file
#         execfile(func_file)
#     if func in locals():
#         # pick func from locals
#         func = locals()[func]
#     else:
#         # pick func from cls
#         func = getattr(cls, func)
#         args = cls + args
#     for key in [key.encode("ASCII") for key in keys]:
#         # load object
#         obj = func(key, *args)
#         obj.register()
#         # register aliases
#         if aliases:
#             obj.register(*aliases.get(key, ()))


def get_object_list(object_type=None):
    """provides all objects in cache in a list"""
    obj_list = [i for k, i in VisibleObject.items()]
    if object_type is not None:
        obj_list = [o for o in obj_list if o._class == object_type]
    return sorted(obj_list, key=repr)
