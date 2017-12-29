# coding=utf-8
""" main test file """

import os, time
times = dict()
times[time.time()] = 'start'

pace_path = os.getcwd()
test_path = pace_path + os.path.sep + 'test'
from test.codeinspection import inspect_module, Logger, PropertyNotInRootException

# code inspection
log = Logger('', ignore_list=[PropertyNotInRootException], stout=True, fileout=False, level='ERROR')
inspect_module('corelibrary', log, base_class_name='VisibleObject', is_root=lambda c: c.__name__.endswith('Interface'))
times[time.time()] = 'inspection'

# run pylint
os.system('pylint corelibrary')
times[time.time()] = 'pylint'

# run sphinx doc
os.chdir(pace_path+'/doc/sphinx')
os.system('sphinx-apidoc -f -e -d 4 -M -o api ../../corelibrary')
os.system('make html')
times[time.time()] = 'sphinx'

# run unittests with coverage
os.chdir(pace_path+'/test')
os.system('coverage run --source corelibrary unit_tests.py')
os.system('coverage report')
times[time.time()] = 'coverage'

# run unit tests
if os.system('python unit_tests.py'):
    raise RuntimeError
times[time.time()] = 'unit tests'

# # run regression tests
# if os.system('python regression_tests.py'):
#     raise RuntimeError
# times[time.time()] = 'regression tests'

# run server tests
# os.chdir(pace_path)
# if os.system('python test/server_tests.py'):
#     raise RuntimeError
# times[time.time()] = 'server tests'

# run performance tests
os.chdir(pace_path)
if os.system('python test/performance_tests.py'):
    raise RuntimeError
times[time.time()] = 'performance tests'

# run memory tests
os.chdir(pace_path)
if os.system('python test/memory_tests.py'):
    raise RuntimeError
times[time.time()] = 'memory tests'

# collect timings
print('\ntimings:')
s = min(times)
o = s
l = max(len(v) for v in times.values())
for t in sorted(times.keys()):
    name = times[t]
    increment = '%d'%(t-o)
    total = '%d'%(t-s)
    args = name.rjust(l), total.rjust(4), increment.rjust(3)
    print('%s:%s (%s) sec.' %args)
    o = t