import iis_bridge.mon as mon
import iis_bridge.site as site
urls = ["http://localhost:80"]
mem_unit = 'MB'
duration = 30 # seconds
reqs_per_sec = 100 # how many request to send per second
datasets = mon.monitor_with_load(duration, urls, reqs_per_sec,\
                                 mem_unit=mem_unit, timeout=15)
mon.html_report(datasets, mem_unit=mem_unit)
print("Done")
