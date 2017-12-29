# coding=utf-8

import test
import os
import sys
import datetime
from unittest import main
from multiprocessing import freeze_support

pace_path = os.getcwd()
test_path = pace_path + os.path.sep + 'test'
if pace_path.endswith('test'):
    test_path = pace_path
    pace_path = test_path[0:-5]
else:
    os.chdir(test_path)

if not sys.path.count(pace_path):
    sys.path.append(pace_path)
    sys.path.insert(0, pace_path)
if not sys.path.count(test_path):
    sys.path.append(test_path)
    sys.path.insert(0, test_path)

if False:
    # debug path env
    print('')
    print('pace_path %s' % pace_path)
    print('test_path %s' % test_path)
    print('')
    for p in sys.path:
        print(' sys.path %s' % p)
    print('')

from instance_unittest import *


if __name__ == '__main__':

    freeze_support()

    start_time = datetime.datetime.now()

    print('')
    print('======================================================================')
    print('')
    print('run %s' % __file__)
    print('in %s' % os.getcwd())
    print('started  at %s' % str(start_time))
    print('')
    print('----------------------------------------------------------------------')
    print('')

    main(verbosity=2)

    print('')
    print('======================================================================')
    print('')
    print('ran %s' % __file__)
    print('in %s' % os.getcwd())
    print('started  at %s' % str(start_time))
    print('finished at %s' % str(datetime.datetime.now()))
    print('')
    print('----------------------------------------------------------------------')
    print('')
