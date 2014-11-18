iis_bridge
==========

is_bridge is a python package for manipulating iis and monitoring iis pools' memory on windows.
It has been tested with python 2.7 on:
- windows server 2008 32 bit
- windows server 2008 R2
- windows server 2012
- windows 7
- windows 8

How to install:
`pip install iis_bridge`

You must run python in a terminal with **administrator privileges** in order to use this package successfully.

Examples:
```
import iis_bridge as iis
# to install iis:
iis.install()

print "iis version %s" % iis.get_version()

# to reset iis:
iis.iisreset()

# to add an iis site on port 5050:
import iis_bridge.site as site
site.create("mysite", 5050, r"C:\inetpub\wwwroot\myapp", "mypool")

# now to list the site names:
print iis.get_site_names()
```

Here is an example how to monitor the private working set memory of all the application pools for 6 seconds while sending 12 GET http requests per second.
The http_report method generates an out.html memory report in the current directory. You can specify output path using the output_path parameter.
```
import iis_bridge.mon as mon
datasets = mon.monitor_with_load(6, 'all', 12)
mon.html_report(datasets)
```

There is a more detailed documentation at: https://pythonhosted.org/iis_bridge/
