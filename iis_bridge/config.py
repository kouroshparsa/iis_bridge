"""
    This module is used for common operations
    as well as global variables
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import os
import subprocess

IIS_HOME = "%s\\Windows\\System32\\inetsrv" % os.getenv("SYSTEMDRIVE")
APP_CMD = "%s\\appcmd.exe" % IIS_HOME
DOCROOT = "%s\\inetpub\\wwwroot" % os.getenv("SYSTEMDRIVE")
LOG_DIR = "%s\\inetpub\\logs\\LogFiles" % os.getenv("SYSTEMDRIVE")
CONFIG_DIR = "%s\\Windows\\System32\\inetsrv\\config" % os.getenv("SYSTEMDRIVE")
WMIC = "%s\\windows\\system32\\wbem\\wmic.exe" % os.getenv('SYSTEMDRIVE')
PIPELINE_MODES = ["Integrated", "Classic"]
IDENTITIES = ["LocalService", "LocalSystem", "NetworkService",\
              "ApplicationPoolIdentity", "Custom"]

def run(cmd):
    """ executes a command, throws exception upon failure
    returns the stdout
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, err = proc.communicate()
    if proc.returncode != 0:
        msg = "%s\n%s\ncmd: %s" % (output, err, cmd)
        raise Exception(msg)
    return output
