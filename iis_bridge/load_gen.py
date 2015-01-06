"""
This module sends some http requests at a specific rate per second
Author: Kourosh Parsa
"""
import threading
from threading import Thread
import time
import urllib2
import urllib
import json

REQUEST_TIMEOUT = 20 # seconds

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


    def send(self, url_obj):
        """ sends a get request to a url
        url: either string or list
            if it is a list, then it specifies [url, req_method, req_data, req_type]
            only the first parameter is required
            req_method could be GET (default), POST, PUT, DELETE, HEAD
            req_type could be html (default), json, xml 
        """
        url = url_obj
        req_method = "GET"
        req_data = None
        req_type = "html"
        if type(url) == list:
            url = url_obj[0]
            if len(url_obj) > 1: req_method = url_obj[1]
            if len(url_obj) > 2: req_data = url_obj[2]
            if len(url_obj) > 3: req_type = url_obj[3]

        try:
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            if req_method in ['PUT', 'POST']:
                if req_type == 'json':
                    if req_data != None:
                        req_data = json.dumps(req_data)
                elif req_type == 'html' and type(req_data) == dict:
                    req_data = urllib.urlencode(req_data) # converts to encoded string
                elif req_type != "xml":
                    raise Exception("The request type %s is not supported yet." % req_type)

                request = urllib2.Request(url, data=req_data)
                if req_type == 'json':
                    request.add_header('Content-Type', 'application/json')
                elif req_type == 'xml':
                    request.add_header('Content-Type', 'text/xml')
            else:
                request = urllib2.Request(url)
        
            request.get_method = lambda: req_method
            resp = opener.open(request, timeout=REQUEST_TIMEOUT)
            print resp.read()
            resp.close()
        except Exception:
            with self.fail_count_lock:
                self.failed_reqs += 1


