import unittest
import iis_bridge as iis
import iis_bridge.site as site
import iis_bridge.pool as pool
import iis_bridge.mon as mon

class TestIis(unittest.TestCase):
    def setup(self):
        iis.install()

    def test_version(self):
        ver = iis.get_version()
        assert len(ver) > 0, "Failed to get the iis version"


    def test_site_pool(self):
        site.create("mysite", 5050, r"C:\inetpub\wwwroot\mysite", "mypool")
        assert "mysite" in iis.get_site_names(), "Failed to create the site"
        assert "mypool" in iis.get_pool_names(), "Failed to create the pool"
        site.delete("mysite")
        pool.delete("mypool")
        assert "mysite" not in iis.get_site_names(), "Failed to delete the site"
        assert "mypool" not in iis.get_pool_names(), "Failed to delete the pool"


    def test_site_pool_state(self):
        site.create("asite", 5060, r"C:\inetpub\wwwroot\asite", "apool")
        site.stop("asite")
        assert not site.is_running("asite"), "Failed to stop the site"
        site.start("asite")
        assert site.is_running("asite"), "Failed to start the site"
        pool.stop("apool")
        assert not pool.is_running("apool"), "Failed to stop the pool"
        pool.start("apool")
        assert pool.is_running("apool"), "Failed to start the pool"
        site.delete("asite")
        pool.delete("apool")


    def test_mem_mon(self):
        datasets = mon.monitor_with_load(6, 'all', 12)
        pointsets = [v[1]['data'] for v in datasets.items()]
        for points in pointsets:
            xvals = [pt[0] for pt in points]
            assert xvals == range(6), "Invalid dataset range: %s" % xvals


    def test_iis_state(self):
        iis.stop()
        assert not iis.is_running(), "Failed to stop iis."
        iis.start()
        assert iis.is_running(), "Failed to start iis."


if __name__ == '__main__':
    unittest.main()