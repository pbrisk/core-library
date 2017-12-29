# coding=utf-8
"""
code inspect logger and formating
"""

from getter import getargsinspect


def args_to_string(argspec):
    res = ""
    defaults = argspec[3]
    args = argspec[0]
    k = len(defaults) if defaults else 0
    n = len(args) - k
    i = 0
    for arg in args:
        res += str(arg)
        if i >= n:
            d = defaults[i - n]
            res += "=" + str(d)
        if arg != args[-1]:
            res += ", "
        i += 1
    return res


def func_to_string(func, cls=None):
    prefix = cls.__name__ + "." if cls else ""
    argsinspect = getargsinspect(func)
    return prefix + func.func_name + "(" + args_to_string(argsinspect) + ")"


class Logger(object):
    def __init__(self, logfile_name='', ignore_list=list(), stout=False, fileout=True, level=''):
        self.logfile_name = logfile_name
        self.log_prefix = ""
        self._error_list = list()
        self._ignore_list = ignore_list
        self._stout = stout
        self._fileout = fileout
        self._loglevel = level
        self.clear()

    def __call__(self, string):
        log_flag = string.startswith(self._loglevel) if self._loglevel else True
        if self.logfile_name and self._fileout and log_flag:
            with open(self.logfile_name, "a") as log:
                log.write(string + "\n")
        if self._stout and log_flag:
            print(string)

    def err(self, obj):
        if type(obj) not in self._ignore_list:
            self._error_list.append(obj)

    def log_errors(self, sort=True):
        self("")
        self("-" * 79)
        self("ERROR LOG")
        self("")

        self._error_list = sorted(self._error_list, key=lambda x: type(x))

        for err in self._error_list:
            msg = "ERROR".ljust(12)
            #msg = ''
            if isinstance(err, Exception):
                msg += str(err)
            elif isinstance(err, str):
                msg += err
            self(msg)

        # sort errors class
        error_dict = dict.fromkeys([type(x) for x in self._error_list])
        for k in sorted(error_dict):
            error_dict[k] = [x for x in self._error_list if type(x) == k]
            self('ERROR of type %s : %d' %(str(k), len(error_dict[k])))

        self("ERRORS IN TOTAL: {}".format(len(self._error_list)))

    def clear(self):
        if self.logfile_name and self._fileout:
            with open(self.logfile_name, "w") as log_file:
                log_file.write("")

    def pre(self, string=""):
        self(self.log_prefix + string)


