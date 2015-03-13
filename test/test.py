import unittest
import iis_bridge as iis
import iis_bridge.site as site
import iis_bridge.pool as pool
import iis_bridge.mon as mon
import iis_bridge.config as config
import time
import os

def get_free_port():
    """ returns an available port number to use """
    port = 5050
    while not site.is_port_available(port):
        port += 1
    return port


def validate_protocols(protocols, bindings):
    for protocol in protocols:
        assert protocol in bindings, "Missing %s protocol" % protocol


class TestIIS(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists('%s\\InetMgr.exe' % config.IIS_HOME):
            iis.install()
        self.test_site = 'test_site'
        count = 2
        while self.test_site in iis.get_site_names():
            self.test_site = "test_site_%i" % count
            count += 1
        self.test_pool = self.test_site.replace("site", "pool")

    def test_version(self):
        ver = iis.get_version()
        assert len(ver) > 0, "Failed to get the iis version"


    def test_site_pool(self):
        site.create(self.test_site, get_free_port(),\
                    r"C:\inetpub\wwwroot\mysite", self.test_pool)
        time.sleep(2)
        assert self.test_site in iis.get_site_names(), "Failed to create the site"
        assert self.test_pool in iis.get_pool_names(), "Failed to create the pool"
        site.delete(self.test_site)
        pool.delete(self.test_pool)
        assert self.test_site not in iis.get_site_names(), "Failed to delete the site"
        assert self.test_pool not in iis.get_pool_names(), "Failed to delete the pool"


    def test_site_pool_state(self):
        site.create(self.test_site, get_free_port(),\
                    r"C:\inetpub\wwwroot\asite", self.test_pool)
        site.stop(self.test_site)
        assert not site.is_running(self.test_site), "Failed to stop the site"
        site.start(self.test_site)
        assert site.is_running(self.test_site), "Failed to start the site"
        pool.stop(self.test_pool)
        assert not pool.is_running(self.test_pool), "Failed to stop the pool"
        pool.start(self.test_pool)
        assert pool.is_running(self.test_pool), "Failed to start the pool"
        site.delete(self.test_site)
        pool.delete(self.test_pool)


    def test_mem_mon(self):
        datasets = mon.monitor_with_load(6, 'all', 12, timeout=40)
        pointsets = [v[1]['data'] for v in datasets.items()]
        for points in pointsets:
            xvals = [pt[0] for pt in points]
            assert xvals == list(range(6)), "Invalid dataset range: %s" % xvals


    def test_iis_state(self):
        iis.stop()
        assert not iis.is_running(), "Failed to stop iis."
        iis.start()
        assert iis.is_running(), "Failed to start iis."

    def test_binding(self):
        port = get_free_port()
        site.create(self.test_site, port,\
                    r"C:\inetpub\wwwroot\asite",\
                    self.test_pool, protocol='https')
        binding = site.get_bindings(self.test_site)
        exp_binding = ["https/:%i:" % port]
        assert binding == exp_binding,\
               "Invalid binding. Expected:%s\nActual:%s"\
               % (exp_binding, binding)

        site.add_binding(self.test_site, 'net.tcp', 808)
        binding = sorted(site.get_bindings(self.test_site))
        exp_binding = sorted(["https/:%i:" % port, "net.tcp/:808:"])
        assert binding == exp_binding,\
               "Invalid binding. Expected:%s\nActual:%s"\
               % (exp_binding, binding)
        site.delete(self.test_site)
        pool.delete(self.test_pool)

    def test_binding_conversion(self):
        bindings = site.convert_site_list_to_binding(\
            'SITE "xxx" (id:21,bindings:http/*:9001:,state:Started)')
        validate_protocols(['http'], bindings)
        assert bindings['http'] == 9001, "Invalid port. Expected: 9001, actual: %s" % bindings['http']
        
        bindings = site.convert_site_list_to_binding(\
            'SITE "xxx" (id:22,bindings:net.pipe/netpipe,http/*:8044:,state:Started)')
        validate_protocols(['net.pipe', 'http'], bindings)
        assert bindings['http'] == 8044, "Invalid port. Expected: 8044, actual: %s" % bindings['http']
        
        bindings = site.convert_site_list_to_binding(\
            'SITE "xxx" (id:23,bindings:http/*:8044:,net.tcp/808:*,net.pipe/netpipe,state:Started)')
        validate_protocols(['net.pipe', 'net.tcp', 'http'], bindings)
        assert bindings['http'] == 8044, "Invalid port. Expected: 8044, actual: %s" % bindings['http']
        
        bindings = site.convert_site_list_to_binding(\
            'SITE "xxx" (id:23,bindings:https/*:8044:,net.tcp/808:*,net.pipe/netpipe,state:Started)')
        validate_protocols(['net.pipe', 'net.tcp', 'https'], bindings)
        assert bindings['https'] == 8044, "Invalid port. Expected: 8044, actual: %s" % bindings['https']


    @classmethod
    def tearDownClass(self):
        site.delete(self.test_site)
        pool.delete(self.test_pool)

if __name__ == '__main__':
    unittest.main()
