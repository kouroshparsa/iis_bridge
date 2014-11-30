"""
    This module is used for enabling the isapi feature
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import xml.etree.ElementTree as et
from iis_bridge.config import *

def enable():
    """ enables isapi """
    cmd = "%s list config /section:system.webServer/security/isapiCgiRestriction"\
        % APP_CMD
    xml = run(cmd)
    has_isapi = False
    has_isapi64 = False
    tree = et.fromstring(xml)
    for element in tree.findall('security/isapiCgiRestriction/add'):
        path = element.get('path')
        if "\\v4.0.30319\\aspnet_isapi.dll" in path:
            if "Framework64" in path:
                has_isapi64 = True
                framework = "Framework64"
            else:
                has_isapi = True
                framework = "Framework"

            if element.get('allowed').lower() == "false":
                run("%s set config /commit:apphost /section:isapiCgiRestriction /-[path='%s']"\
                    % (APP_CMD, path))
                path = "%windir%\\Microsoft.NET\\%s\\v4.0.30319\\aspnet_isapi.dll" % framework
                run("%s set config /commit:apphost /section:isapiCgiRestriction /+[path='%s',allowed='True']"\
                    % (APP_CMD, path))

    if not has_isapi:
        path = "%windir%\\Microsoft.Net\\Framework\\v4.0.30319\\aspnet_isapi.dll"
        run("%s set config /commit:apphost /section:isapiCgiRestriction /+[path='%s',allowed='True']"\
            % (APP_CMD, path))


    if not has_isapi64:
        path = "%windir%\\Microsoft.Net\\Framework64\\v4.0.30319\\aspnet_isapi.dll"
        run("%s set config /commit:apphost /section:isapiCgiRestriction /+[path='%s',allowed='True']"\
            % (APP_CMD, path))
