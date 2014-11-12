"""
This module sends some http requests at a specific rate per second
Author: Kourosh Parsa
"""
import threading
from threading import Thread
import time
import urllib2

class HttpFlood(Thread):
    """ sends parallel get requests to the specified urls
    at a constant rate per second
    It's non-blocking - it does not wait for the response
	Parameters:
	iterations: how many iterations to perform (load duration)
	urls: list of urls to send requests to
	rate: an integer representing how many requests to send per second
    interval: time steps in seconds!
	load_type: how to generate the http load, default=constant
    """
    LOAD_TYPES = ['constant', 'step']
    
    def __init__(self, iterations, urls, rate,\
        interval=1, load_type=LOAD_TYPES[0]):
        self.failed_reqs = 0
        self.fail_count_lock = threading.Lock()
        super(HttpFlood, self).__init__()
        self.iterations = iterations
        self.urls = urls
        self.rate = rate
        self.interval = interval
        self.load_type = load_type


    def run(self):
        if len(self.urls) < 1:
            raise Exception("You must supply at least one url.")
        threads = []
        ind = 0
        if self.load_type == 'step':
            self.iterations /= 2
            time.sleep(self.iterations)# first half, silence

        for i in range(self.iterations / self.interval):
            for j in range(self.rate):
                thread = threading.Thread(target=self.send, args=[self.urls[ind]])
                thread.daemon = True # Daemonize thread
                thread.start() # Start the execution
                threads.append(thread)
                ind = (ind + 1) % len(self.urls)
            threads = [t for t in threads if t.isAlive()]# clean up
            time.sleep(self.interval)
        for thread in threads:
            thread.join()
        threads = []# clean up


    def send(self, url):
        """ sends a get request to a url """
        try:
            response = urllib2.urlopen(url)
            if response.getcode() != 200:
                with self.fail_count_lock:
                    self.failed_reqs += 1
            response.close()
        except Exception:
            with self.fail_count_lock:
                self.failed_reqs += 1


