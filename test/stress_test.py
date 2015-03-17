import iis_bridge.mon as mon
import iis_bridge.site as site
urls = ["http://localhost:80"]
mem_unit = 'MB'
duration = 30 # seconds
reqs_per_sec = 100 # how many request to send per second
datasets = mon.monitor_with_load(duration, urls, reqs_per_sec,\
                                 mem_unit=mem_unit, timeout=15)
from datetime import datetime
curr_time = str(datetime.now().replace(microsecond=0))
mon.html_report(datasets, mem_unit=mem_unit, top_txt=curr_time)
print("Done")
