# To detect memory leaks or extraordinarily increasing computation time

import unittest
import cProfile
import gc
import json
import matplotlib
import os
import pstats
import psutil
import sys

from datetime import datetime

matplotlib.use('agg')
import matplotlib.pyplot as plt

sys.path.append('.')
import corelibrary

# HELPER #############################################################

def obj_num():
    objs = gc.get_objects()
    obnumdict = dict()
    for o in objs:
        if str(type(o)) not in obnumdict:
            obnumdict[str(type(o))] = 1
        else:
            obnumdict[str(type(o))] += 1

    return obnumdict


def mem(process):
    """ mem """
    mem_in_GB = process.memory_info()[0] / 2. ** 30
    rel_mem = process.memory_percent()
    return rel_mem, mem_in_GB


# TESTS ##############################################################

class ObjLoadingTest(unittest.TestCase):
    PATH = 'test/product_unittest.json'
    PROFILING_DIR = 'test/profile'
    TESTFUNC = lambda: corelibrary.VisibleObject.load_objects_from_file(ObjLoadingTest.PATH, True)

    @staticmethod
    def make_plots(data, directory=PROFILING_DIR, top=-1):

        TIME = datetime.now().strftime('%Y%m%d_%H%M%S')

        fig = plt.figure()
        fig.add_subplot(111, title='Mem Use in %')
        plt.plot(data[0], data[1])
        plt.savefig(directory + '/{}_mem_use_in_percent.png'.format(TIME))

        fig = plt.figure()
        fig.add_subplot(111, title='Mem Use in GB')
        plt.plot(data[0], data[2])
        plt.savefig(directory + '/{}_mem_use_in_GB.png'.format(TIME))

        fig = plt.figure(figsize=(15, 10))
        topobs = [x[0] for x in sorted(data[3][-1].items(), key=lambda x: x[1], reverse=True)][0:top]

        topob_dev = dict()
        for t in topobs:
            topob_dev[t] = list()
            for d in data[3]:
                topob_dev[t].append(d.get(t, 0))

        fig.add_subplot(111, title="TOP {} gc tracked Objs".format(top))
        for k in topob_dev:
            plt.plot(topob_dev[k], label=k)

        plt.legend(loc=2)
        plt.savefig(directory + '/{}_TOP_tracked_objs.png'.format(TIME))

        fig = plt.figure(figsize=(15, 10))
        fig.add_subplot(111, title="time to load")
        plt.plot(data[0], data[4])

        plt.savefig(directory + '/{}_loading_times.png'.format(TIME))

    def test_mem_leak(self, max_abs_mem=None, max_cnt=50, test_func=TESTFUNC, profiling_directory=PROFILING_DIR):

        if max_abs_mem == None:
            max_abs_mem = max_cnt * 4e-5 + 2e-3

        TIME = datetime.now().strftime('%Y%m%d_%H%M%S')

        if not os.path.isdir(profiling_directory):
            os.makedirs(profiling_directory)

        time_profile = profiling_directory + '/test_mem_time.prof.temp'
        data_json_name = profiling_directory + '/profiling_data_{}.json'.format(TIME)

        pid = os.getpid()
        py = psutil.Process(pid)
        initial_abs_mem = mem(py)[1]
        abs_mem = initial_abs_mem

        cnt = 0
        with open(data_json_name, 'w') as data:
            data.write('[\n')

            difference = abs_mem - initial_abs_mem
            self.assertLessEqual(difference, max_abs_mem)
            while difference < max_abs_mem and cnt < max_cnt:

                if cnt > 0:
                    data.write(',\n')

                cProfile.runctx('test_func()', globals(), {'test_func': test_func}, filename=time_profile)

                all_stats = False
                stats_num = cnt if all_stats else 0
                stats_name = profiling_directory + '/{}_stats_{}.txt'.format(TIME, stats_num)
                with open(stats_name, 'w') as stat_file:
                    stats = pstats.Stats(time_profile, stream=stat_file)
                    stats.strip_dirs()
                    stats.sort_stats('tottime')
                    stats.print_stats()

                rel_mem, abs_mem = mem(py)
                difference = abs_mem - initial_abs_mem
                self.assertLessEqual(difference, max_abs_mem)

                iteration_data = (cnt, rel_mem, difference, obj_num(), stats.total_tt)
                data.write(json.dumps(iteration_data, indent=2))

                cnt += 1

            data.write('\n]')

        with open(data_json_name, 'r') as data_file:
            data = json.load(data_file)
            data = [[d[i] for d in data] for i in range(0, 5)]
            self.__class__.make_plots(data, top=10)
