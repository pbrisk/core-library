import cProfile
import gc
import os
import pstats
import time
from datetime import datetime
import json
import dill as pickle
import sys
import unittest
import psutil
import sys

import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt

sys.path.append('.')
import corelibrary

PATH = 'test/product_unittest.json'
PROFILING_DIR = 'test/profile'


def profile_loading(test_file_path, profiling_directory=PROFILING_DIR, runs=1, profiling_steps=100):
    if not os.path.isdir(profiling_directory):
        os.makedirs(profiling_directory)

    for i in range(0, runs):
        print 'RUN No. %i' % i
        if i % profiling_steps == 0:
            print ' ... PROFILING'

            # filename creation for profiling
            test_file_name = os.path.split(test_file_path)[1].replace('.', '_')
            target_name = "/{name}_profiling{num:0>{length}}".format(name=test_file_name, num=i, length=len(str(runs)))
            profiling_file_raw = profiling_directory + target_name + ".prof"
            profiling_file_csv = profiling_directory + target_name + ".csv"
            profiling_stats = profiling_directory + target_name + ".txt"

            cProfile.runctx('corelibrary.VisibleObject.load_objects_from_file(file, True)',
                            globals=globals(), locals={'file': test_file_path}, filename=profiling_file_raw)
            with open(profiling_file_csv, 'w') as f, open(profiling_stats, 'w') as g:
                stats = pstats.Stats(profiling_file_raw, stream=g)
                stats.strip_dirs()
                stats.sort_stats('tottime')
                stats.print_stats()
                f.write("FILE; LINE; NAME; CC; NC; TotalTime; CumulatedTime\n")
                for k in sorted(stats.stats.keys()):
                    func = ';'.join(map(str, list(k)))
                    stat = ';'.join(map(str, list(stats.stats[k][0:4]))).replace('.', ',')
                    f.write(';'.join([func, stat]))
                    f.write('\n')
        else:
            corelibrary.VisibleObject.load_objects_from_file(test_file_path, True)


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


def test_mem_leak(max_rel_mem=30, max_cnt=300, test_func=(lambda: None), profiling_directory=PROFILING_DIR,
                  all_stats=False, visible_progress=False):
    TIME = datetime.now().strftime('%Y%m%d_%H%M%S')

    if not os.path.isdir(profiling_directory):
        os.makedirs(profiling_directory)

    time_profile = profiling_directory + '/test_mem_time.prof.temp'
    data_json_name = profiling_directory + '/profiling_data_{}.json'.format(TIME)

    pid = os.getpid()
    py = psutil.Process(pid)
    rel_mem = mem(py)[0]
    data = list()
    cnt = 0

    with open(data_json_name, 'w') as data:
        data.write('[\n')

        while rel_mem < max_rel_mem and cnt < max_cnt:

            if cnt > 0:
                data.write(',\n')

            cProfile.runctx('test_func()', globals(), {'test_func': test_func}, filename=time_profile)

            if cnt % 50 == 0:
                corelibrary.VisibleObject().clean_up_link_dict()

            stats_num = cnt if all_stats else 0
            stats_name = profiling_directory + '/{}_stats_{}.txt'.format(TIME, stats_num)
            with open(stats_name, 'w') as stat_file:
                stats = pstats.Stats(time_profile, stream=stat_file)
                stats.strip_dirs()
                stats.sort_stats('tottime')
                stats.print_stats()

            rel_mem, abs_mem = mem(py)
            iteration_data = (cnt, rel_mem, abs_mem, obj_num(), stats.total_tt)
            data.write(json.dumps(iteration_data, indent=2))

            if visible_progress:
                print cnt, '/', max_cnt, 'mem:', abs_mem, 'GB (', rel_mem, '% )'

            # time_peaks = 0
            # if cnt > 1 and abs(t/data[-2][-1])>1.2:
            #     time_peaks +=1
            #     stats_name = profiling_directory + '/{}_time_peak_{}.txt'.format(TIME, time_peaks)
            #     with open(stats_name, 'w') as stat_file:
            #         stats = pstats.Stats(time_profile, stream=stat_file)
            #         stats.strip_dirs()
            #         stats.sort_stats('tottime')
            #         stats.print_stats()

            cnt += 1
            # print cnt, rel_mem, sys.getsizeof(data)

        data.write('\n]')

    return data_json_name


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
    m = sum(data[4]) / float(len(data[0]))
    plt.plot(data[0], [m for _ in data[0]])

    plt.savefig(directory + '/{}_loading_times.png'.format(TIME))


if __name__ == "__main__":
    # corelibrary.RateIndex('EUR-EONIA').register()
    # corelibrary.RateIndex('DISC').register()
    # corelibrary.RateIndex('EURIBOR').register()
    # corelibrary.RateIndex('EUR-EURIBOR-3M').register()
    # corelibrary.FixingTable().register()

    testfunc = lambda: corelibrary.VisibleObject.load_objects_from_file(PATH, True)

    data_json_name = test_mem_leak(test_func=testfunc, max_cnt=100, visible_progress=True)
    # data_json_name = PROFILING_DIR + '/profiling_data_20170905_091729.json'
    with open(data_json_name, 'r') as data_file:
        data = json.load(data_file)
        data = [[d[i] for d in data] for i in range(0, 5)]
        make_plots(data, top=10)
