"""
    This module is used for common operations
    as well as global variables
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import os
import subprocess
import platform

IIS_HOME = "%s\\Windows\\System32\\inetsrv" % os.getenv("SYSTEMDRIVE")
APP_CMD = "%s\\appcmd.exe" % IIS_HOME
DOCROOT = "%s\\inetpub\\wwwroot" % os.getenv("SYSTEMDRIVE")
LOG_DIR = "%s\\inetpub\\logs\\LogFiles" % os.getenv("SYSTEMDRIVE")
PIPELINE_MODES = ["Integrated", "Classic"]
IDENTITIES = ["LocalService", "LocalSystem", "NetworkService",\
              "ApplicationPoolIdentity", "Custom"]
NET_DIR = "%s\\Windows\\Microsoft.NET" % os.getenv("SYSTEMDRIVE")
if platform.machine().endswith("64") and\
    platform.architecture()[0].startswith("32"):
    # 64 windows with 32 bit python - disable wow64
    DISM = "%s\\Windows\sysnative\\Dism.exe" % os.getenv("SYSTEMDRIVE")
    CONFIG_DIR = "%s\\Windows\\sysnative\\inetsrv\\config" % os.getenv("SYSTEMDRIVE")
    WMIC = "%s\\Windows\\sysnative\\wbem\\wmic.exe" % os.getenv('SYSTEMDRIVE')
    SERVER_MGR_CMD = "%s\\windows\\sysnative\\ServerManagerCmd.exe" % os.getenv('SYSTEMDRIVE')
else:
    DISM = "%s\\Windows\System32\\Dism.exe" % os.getenv("SYSTEMDRIVE")
    CONFIG_DIR = "%s\\Windows\\System32\\inetsrv\\config" % os.getenv("SYSTEMDRIVE")
    WMIC = "%s\\Windows\\system32\\wbem\\wmic.exe" % os.getenv('SYSTEMDRIVE')
    SERVER_MGR_CMD = "%s\\windows\\system32\\ServerManagerCmd.exe" % os.getenv('SYSTEMDRIVE')

if not os.path.exists(DISM):
    DISM = None

def run(cmd, errMsg=None):
    """ executes a command, throws exception upon failure
    returns the stdout as string
    cmd: string - command to run
    errMsg: string (default=None) - the error message to display
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, err = proc.communicate()
    if type(output) == bytes:
        output = output.decode(encoding='UTF-8')
    if "[Error]" in output or proc.returncode != 0:
        if errMsg:
            raise Exception(errMsg)
        else:
            raise Exception("%s\r\n%s" % (output, err))
    return output
