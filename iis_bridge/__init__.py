"""
    This module initializes the iis_bridge package
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import iis_bridge.config as config
import sys
import os
import subprocess
import _winreg
import platform

def iisreset():
    """ resets iis
    """
    config.run('iisreset')


def is_running(name):
    """ returns a boolean indicating whether iis is running
    """
    return get_status() == "running"


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


def is_older_than_2008r2():
    """ returns a boolean indicating whether
    the platform is older than windows server 2008 R2 """
    return sys.getwindowsversion().major < 6 or \
        (sys.getwindowsversion().major == 6 \
        and sys.getwindowsversion().minor < 1)


def install(packages=None):
    """ installs iis
    Parameters
    --------
    packages: list. The iis features (package names)
    """

    # for windows vista and up (windows 7, windows 8, windows server 2012):
    dism_pkgs = ["IIS-WebServerRole", "IIS-WebServer", "IIS-CommonHttpFeatures",\
                 "IIS-Security", "IIS-RequestFiltering", "IIS-StaticContent",\
                 "IIS-DefaultDocument", "IIS-DirectoryBrowsing", "IIS-HttpErrors",\
                 "IIS-HttpRedirect", "IIS-WebDAV", "IIS-ApplicationDevelopment",\
                 "IIS-WebSockets", "IIS-ApplicationInit", "IIS-NetFxExtensibility",\
                 "IIS-NetFxExtensibility45", "IIS-ISAPIExtensions", "IIS-ISAPIFilter",\
                 "IIS-ASPNET", "IIS-ASPNET45", "IIS-ASP", "IIS-CGI", "IIS-ServerSideIncludes",\
                 "IIS-HealthAndDiagnostics", "IIS-HttpLogging", "IIS-LoggingLibraries",\
                 "IIS-RequestMonitor", "IIS-HttpTracing", "IIS-CustomLogging",\
                 "IIS-ODBCLogging", "IIS-CertProvider", "IIS-BasicAuthentication",\
                 "IIS-WindowsAuthentication", "IIS-DigestAuthentication",\
                 "IIS-ClientCertificateMappingAuthentication", "IIS-IISCertificateMappingAuthentication",\
                 "IIS-URLAuthorization", "IIS-IPSecurity", "IIS-Performance", "IIS-HttpCompressionStatic",\
                 "IIS-HttpCompressionDynamic", "IIS-WebServerManagementTools", "IIS-ManagementConsole",\
                 "IIS-LegacySnapIn", "IIS-ManagementScriptingTools", "IIS-ManagementService",\
                 "IIS-IIS6ManagementCompatibility", "IIS-Metabase", "IIS-WMICompatibility",\
                 "IIS-LegacyScripts", "IIS-FTPServer", "IIS-FTPSvc", "IIS-FTPExtensibility",\
                 "WAS-WindowsActivationService", "WAS-ProcessModel", "WAS-NetFxEnvironment",\
                 "WAS-ConfigurationAPI", "IIS-HostableWebCore"]
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

    if is_older_than_2008r2():
        if not packages:
            packages = ["Web-Server"]
        for pkg in packages:
            try:
                config.run("%s -install %s" % (config.SERVER_MGR_CMD, pkg))
                print("Installed %s -allSubFeatures " % pkg)
            except Exception as ex:
                if "NoChange" in str(ex):
                    print("%s is already installed." % pkg)
                else:
                    raise Exception(str(ex))
    elif config.DISM:
        if not packages:
            packages = dism_pkgs
        for pkg in packages:
            config.run("%s /online /Enable-Feature /FeatureName:%s /All"\
                    % (config.DISM, pkg))
            print("Installed %s" % pkg)
    elif packages:
        if type(packages) == list:
            packages_str = ";".join(packages)
        print("Installing %s" % packages_str)
        config.run("start /w pkgmgr /iu:%s" % packages_str)
    else:
        print("Installing %s" % professional_pkg)
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
    framework_dir = "%s\\Framework"\
        % (config.NET_DIR, os.getenv('SYSTEMDRIVE'))
    versions = ["v2.0.50727", "v4.0.30319"]
    for ver in versions:
        aspnet_regiis = os.path.join(framework_dir, ver, 'aspnet_regiis.exe')
        if os.path.exists(aspnet_regiis):
            cmd = "%s -ir" % aspnet_regiis
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            out, err = proc.communicate()
            if proc.returncode != 0:
                print("Error: %s\n%s" % (out, err))
        else:
            print("Could not register %s because the file is missing: %s"\
                % (ver, aspnet_regiis))
        config.run("%s /Online /Enable-Feature /all /FeatureName:IIS-ASPNET45" % config.DISM)


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


def install_wcf(components="all"):
    """ install wcf services
    Parameters
    components: (optional string or list) default=all,
    are the components of wcf to install
    """
    if is_older_than_2008r2():
        raise Exception("WCF is not supported on windows "\
                        "older than win server 2008 R2")
    VALID_COMPS = ["WCF-Services45", "WCF-HTTP-Activation45",\
        "WCF-TCP-Activation45", "WCF-Pipe-Activation45",\
        "WCF-MSMQ-Activation45", "WCF-TCP-PortSharing45",\
        "WCF-HTTP-Activation", "WCF-NonHTTP-Activation"]
    if components == "all":
        install(VALID_COMPS)
    else:
        if type(components) == str:
            components = [components]
        install(components)

