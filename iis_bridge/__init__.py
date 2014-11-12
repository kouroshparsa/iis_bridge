"""
    This module initializes the iis_bridge package
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import iis_bridge.config as config
import sys
import os
import subprocess
import _winreg

def iisreset():
    """ resets iis
    """
    config.run('iisreset')

def get_status():
    """ gets the iis status {stopped, running} """
    output = config.run('iisreset /status')
    if "Running" in output:
        return "running"
    else:
        return "stopped"


def stop():
    """ stops iis
    """
    if get_status() == "running":
        config.run('iisreset /stop')


def start():
    """ starts iis
    """
    if get_status() == "stopped":
        config.run('iisreset /start')


def install(packages=None):
    """ installs iis
    Parameters
    --------
    packages: string. The iis feature (package) names separated by semicolon
    """
    if sys.getwindowsversion().major < 6 or \
        (sys.getwindowsversion().major == 6 \
        and sys.getwindowsversion().minor < 1):
        raise Exception("iis install is not yet supported "\
            "on windows older than windows server 2008 R2")
        # because pkgmgr is not supported on platforms before win2k8 R2
        #config.run("start /w pkgmgr /iu:Web-Server")
    else:
        config.run("start /w pkgmgr /iu:IIS-WebServerRole;WAS-WindowsActivationService;WAS-ProcessModel;WAS-NetFxEnvironment;WAS-ConfigurationAPI")

    professional_pkg = "IIS-WebServerRole;IIS-WebServer;IIS-CommonHttpFeatures;IIS-StaticContent;IIS-DefaultDocument;IIS-DirectoryBrowsing;"\
        "IIS-HttpErrors;IIS-HttpRedirect;IIS-ApplicationDevelopment;IIS-ASPNET;IIS-NetFxExtensibility;IIS-ASP;IIS-CGI;"\
        "IIS-ISAPIExtensions;IIS-ISAPIFilter;IIS-ServerSideIncludes;IIS-HealthAndDiagnostics;IIS-HttpLogging;IIS-LoggingLibraries;"\
        "IIS-RequestMonitor;IIS-HttpTracing;IIS-CustomLogging;IIS-ODBCLogging;IIS-Security;IIS-BasicAuthentication;"\
        "IIS-WindowsAuthentication;IIS-DigestAuthentication;IIS-ClientCertificateMappingAuthentication;"\
        "IIS-IISCertificateMappingAuthentication;IIS-URLAuthorization;IIS-RequestFiltering;IIS-IPSecurity;"\
        "IIS-Performance;IIS-HttpCompressionStatic;IIS-HttpCompressionDynamic;IIS-WebServerManagementTools;"\
        "IIS-ManagementConsole;IIS-ManagementScriptingTools;IIS-ManagementService;IIS-IIS6ManagementCompatibility;"\
        "IIS-Metabase;IIS-WMICompatibility;IIS-LegacyScripts;IIS-LegacySnapIn;IIS-FTPPublishingService;IIS-FTPServer;"\
        "IIS-FTPManagement;WAS-WindowsActivationService;WAS-ProcessModel;WAS-NetFxEnvironment;WAS-ConfigurationAPI"
    premium_pkg = "IIS-WebServerRole;IIS-WebServer;IIS-CommonHttpFeatures;IIS-StaticContent;IIS-DefaultDocument;"\
        "IIS-DirectoryBrowsing;IIS-HttpErrors;IIS-HttpRedirect;IIS-ApplicationDevelopment;IIS-ASPNET;"\
        "IIS-NetFxExtensibility;IIS-ASP;IIS-CGI;IIS-ISAPIExtensions;IIS-ISAPIFilter;IIS-ServerSideIncludes;"\
        "IIS-HealthAndDiagnostics;IIS-HttpLogging;IIS-LoggingLibraries;IIS-RequestMonitor;IIS-HttpTracing;"\
        "IIS-CustomLogging;IIS-Security;IIS-BasicAuthentication;IIS-URLAuthorization;IIS-RequestFiltering;"\
        "IIS-IPSecurity;IIS-Performance;IIS-HttpCompressionStatic;IIS-HttpCompressionDynamic;"\
        "IIS-WebServerManagementTools;IIS-ManagementConsole;IIS-ManagementScriptingTools;IIS-ManagementService;"\
        "IIS-IIS6ManagementCompatibility;IIS-Metabase;IIS-WMICompatibility;IIS-LegacyScripts;IIS-LegacySnapIn;"\
        "WAS-WindowsActivationService;WAS-ProcessModel;WAS-NetFxEnvironment;WAS-ConfigurationAPI"

    if packages:
        config.run("start /w pkgmgr /iu:%s" % packages)
    else:
        cmd = "start /w pkgmgr /iu:%s" % professional_pkg
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        proc.wait()
        if proc.returncode != 0:
            cmd = "start /w pkgmgr /iu:%s" % premium_pkg
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            proc.wait()
            if proc.returncode != 0:
                raise Exception("Failed to install some iis packages.")


def register_asp():
    """ installs and registers asp.net on iis """
    framework_dir = "%s\\Windows\\Microsoft.NET\\Framework"\
        % os.getenv('SYSTEMDRIVE')
    versions = ["v2.0.50727", "v4.0.30319"]
    for ver in versions:
        aspnet_regiis = os.path.join(framework_dir, ver, 'aspnet_regiis.exe')
        if os.path.exists(aspnet_regiis):
            cmd = "%s -ir" % aspnet_regiis
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            out, err = proc.communicate()
            if proc.returncode != 0:
                print "Error: %s\n%s" % (out, err)
        else:
            print "Could not register %s because the file is missing: %s"\
                % (ver, aspnet_regiis)
        config.run("dism.exe /Online /Enable-Feature /all /FeatureName:IIS-ASPNET45")


def get_version():
    """ returns the iis version as string """
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,\
        r'SOFTWARE\Microsoft\InetStp',\
        0, _winreg.KEY_WOW64_64KEY + _winreg.KEY_ALL_ACCESS)
    ver = _winreg.QueryValueEx(key, "VersionString")[0]
    ver = str(ver.split(' ')[1])
    return ver


def get_pool_names():
    """ returns a list of application pool names """
    cmd = "%s list apppool" % config.APP_CMD
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, err = proc.communicate()
    if proc.returncode != 0:
        raise Exception("You need elevated permissions.")
    return [line.split('"')[1] for line in output.splitlines()]


def get_site_names():
    """ returns a list of site names """
    cmd = "%s list sites" % config.APP_CMD
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    if proc.returncode != 0:
        raise Exception("You need elevated permissions.")
    return [line.split('"')[1] for line in output.splitlines()]

