"""
    This module monitors iis worker memory consumption
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import os
import sys
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

    for t in range(total_length):
        workers = mem.get_workers(mem_type=mem_type, mem_unit=mem_unit)
        t2 = delta * t
        for worker in workers:
            if not datasets.has_key(worker.poolname):
                datasets[worker.poolname] =\
                    {'label': worker.poolname, 'data': []}
            datasets[worker.poolname]['data'].append(\
                [t2, worker.mem])
        time.sleep(delta)
    return datasets


def monitor_with_load(iterations, urls, rate,\
        mem_type='WorkingSetPrivate', mem_unit='KB'):
    """ generates an http load and monitors the memory consumption
    iterations: how many iterations to perform (load duration)
    urls: list of urls to send requests to
    rate: an integer representing how many requests to send per second
    mem_type: (optional) what type of memory you'd like to monitor
    mem_unit: (optional) the memory units
    output_path: where to save the html report
    """
    if urls == 'all':
        urls = [site.get_url(name) for name in iis.get_site_names()]
    interval = 1 # per second
    http_thread = load_gen.HttpFlood(iterations, urls, rate, interval=interval)
    http_thread.start()
    print "Starting to send http requests and monitor the memory usage..."
    datasets = monitor(total_length=iterations,\
        mem_type=mem_type, mem_unit=mem_unit, delta=interval)
    http_thread.join()
    print "Failed requests: %i" % http_thread.failed_reqs
    return datasets


def html_report(datasets, mem_type='WorkingSetPrivate', mem_unit='KB',\
         output_path='out.html'):
    """ produces an html report
    datasets: the data to plot along with labels
    mem_type: (optional) what type of memory you'd like to monitor
    mem_unit: (optional) the memory units
    output_path: where to save the html report
    """
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
    print "The html report is saved to %s" % os.path.realpath(output_path)


if __name__ == "__main__":
    mem_type = 'WorkingSetPrivate'
    mem_unit = 'MB'
    datasets = monitor_with_load(6, 'all', 8,\
        mem_type=mem_type, mem_unit=mem_unit)
    html_report(datasets, mem_type=mem_type, mem_unit=mem_unit)
