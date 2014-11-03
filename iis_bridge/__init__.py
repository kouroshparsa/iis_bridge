"""
    This module initializes the iis_bridge package
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import subprocess

def iisreset():
    """ resets iis
    """
    proc = subprocess.Popen("iisreset", shell=True, stdout=subprocess.PIPE)
    output, err = proc.communicate()
    if proc.returncode != 0:
        raise Exception("%s\n%s" % (output, err))