"""
    This module monitors iis worker memory consumption
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import os
import sys
import copy
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FILE = os.path.join(\
    BASE_DIR, 'templates', 'template1.html')
sys.path.append(os.path.realpath("%s/.." % BASE_DIR))
import iis_bridge as iis
from jinja2 import Environment as JinjaEnvironment
import time
import iis_bridge.mem as mem
import iis_bridge.load_gen as load_gen
import iis_bridge.site as site

def monitor(delta=1, total_length=10,\
        mem_type='WorkingSetPrivate', mem_unit='KB'):
    """ monitors app pools
    Parameters:
    delta: time steps in seconds
    total_length: total duration in seconds
    """
    datasets = {}
    POOL_NAMES = iis.get_pool_names()
    for t in range(total_length):
        workers = mem.get_workers(mem_type=mem_type, mem_unit=mem_unit)
        t2 = delta * t
        pools_without_workers = copy.copy(POOL_NAMES)
        for worker in workers:
            pools_without_workers.remove(worker.poolname)
            if worker.poolname not in datasets:
                datasets[str(worker.poolname)] =\
                    {'label': str(worker.poolname), 'data': []}
            datasets[worker.poolname]['data'].append(\
                [t2, worker.mem])
        for p in pools_without_workers:
            if p in datasets:
                datasets[p]['data'].append([t2, 0])
            else:
                datasets[p] = {'label': str(p), 'data': [[t2, 0]]}
        time.sleep(delta)
    return datasets


def monitor_with_load(iterations, urls, rate,\
        mem_type='WorkingSetPrivate', mem_unit='KB', timeout=15):
    """ generates an http load and monitors the memory consumption
    iterations: how many iterations to perform (load duration)
    urls: list of urls to send requests to
    rate: an integer representing how many requests to send per second
    mem_type: (optional) what type of memory you'd like to monitor
    mem_unit: (optional) the memory units
    timeout: http request timeout in second
    output_path: where to save the html report
    """
    if urls == 'all':
        urls = [site.get_url(name) for name in iis.get_site_names()]
    interval = 1 # per second
    http_thread = load_gen.HttpFlood(iterations,\
        urls, rate, interval=interval, timeout=timeout)
    http_thread.daemon = True
    http_thread.start()
    print("Starting to send http requests and monitor the memory usage...")
    datasets = monitor(total_length=iterations,\
        mem_type=mem_type, mem_unit=mem_unit, delta=interval)
    http_thread.join()
    print("%i/%i requests Failed."\
          % (http_thread.failed_reqs, int(rate * iterations / interval)))
    return datasets


def html_report(datasets, mem_type='WorkingSetPrivate', mem_unit='KB',\
         output_path='out.html', pools_to_monitor=None):
    """ produces an html report
    datasets: the data to plot along with labels
    mem_type: (optional) what type of memory you'd like to monitor
    mem_unit: (optional) the memory units
    output_path: where to save the html report
    """
    if pools_to_monitor:
        datasets = dict((k,v) for k, v in datasets.items() if k in pools_to_monitor)
    datasets = dict((str(k),v) for k, v in datasets.items())
    for val in datasets.values():
        if 'label' in val:
            val['label'] = str(val['label'])

    context = {
        'datasets': datasets,
        'xlabel': 'time (seconds)',
        'ylabel': '%s (%s)' % (mem_type, mem_unit)
    }
    source = open(TEMPLATE_FILE, 'r').read()
    jinja_template = JinjaEnvironment().from_string(source)
    out = jinja_template.render(context)
    out_file = open(output_path, 'w')
    out_file.write(out)
    out_file.close()
    print("The html report is saved to %s" % os.path.realpath(output_path))


if __name__ == "__main__":
    mem_type = 'WorkingSetPrivate'
    mem_unit = 'MB'
    datasets = monitor_with_load(6, 'all', 8,\
        mem_type=mem_type, mem_unit=mem_unit)
    html_report(datasets, mem_type=mem_type, mem_unit=mem_unit)
