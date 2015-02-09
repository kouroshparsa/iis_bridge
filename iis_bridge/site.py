"""
    This module is used for manipulating iis sites
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import iis_bridge.config as config
import iis_bridge
from iis_bridge import pool as pool
import subprocess
import time

def is_port_available(port):
    """ returns a boolean indicating whether the port is
    being used by any program
    Parameters:
    - port: int
    """
    cmd = "netstat -an|findstr \"0.0.0.0:%s\"" % port
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    proc.communicate()
    return proc.returncode != 0


def is_port_taken(port):
    """ returns a boolean indicating whether the port is
    being used by any iis site
    Parameters:
    - port: int
    """
    cmd = "%s list sites" % config.APP_CMD
    output = config.run(cmd)
    return "/*:%s:," % port in output


def get_port(site_name):
    """ Given the iis site name
    it returns the port number of the site - integer
    """
    cmd = "%s list sites|findstr \"%s\"" % (config.APP_CMD, site_name)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, err = proc.communicate()
    if proc.returncode != 0:
        raise config.runtimeError("The site [%s] does not exist. %s"\
            % (site_name, err))
    port = output.split(":")[3]
    return int(port)


def get_url(site_name):
    """ Given the iis site name
    it returns the site url
    """
    cmd = "%s list sites|findstr \"%s\"" % (config.APP_CMD, site_name)
    output = str(subprocess.check_output(cmd, shell=True))
    protocol = "http"
    if "https" in output:
        protocol = "https"
    port = output.split(":")[3]
    url = "%s://localhost:%s/" % (protocol, port)
    return url


def exists(name):
    """ given the site name, returns whether
    the site already exists
    """
    cmd = "%s list sites" % config.APP_CMD
    output = config.run(cmd)
    for line in output.splitlines():
        if line.split('"')[1] == name:
            return True
    return False


def create(name, port, path, pool_name, protocol="http", site_id=None, ip='', host=''):
    """ creates a new iis site
    Parameters:
    - name: site name
    - port: port number
    - path: the directory where your web app is
    - pool_name: pool name to associate with the site
    - protocol (optional): http, https
    - site_id (optional): the site id to associate with the new site
    """
    if exists(name):
        print("The site '%s' already exists." % name)
        return

    if is_port_taken(port):
        raise Exception("An iis site is already using the port: %i" % port)
    if not is_port_available(port):
        raise Exception("A program is already using the port: %i" % port)

    if not pool.exists(pool_name):
        pool.create(pool_name)
        for iter in range(5):# wait a bit
            if pool.exists(pool_name):
                break
            time.sleep(1)
    cmd = "%s add site /name:\"%s\" /physicalPath:\"%s\" /bindings:%s/%s:%i:%s"\
          % (config.APP_CMD, name, path, protocol, host, port, ip)
    if site_id:
        cmd = "%s /id:%i" % (cmd, site_id)
    config.run(cmd)
    config.run("%s set app \"%s/\" /applicationPool:\"%s\""\
        % (config.APP_CMD, name, pool_name))
    for iter in range(5):# wait a bit
        if exists(name):
            break
        time.sleep(1)


def delete(name):
    """ deletes a site given its name """
    if not exists(name):
        print("The site '%s' does not exist." % name)
        return

    cmd = "%s delete site \"%s\"" % (config.APP_CMD, name)
    config.run(cmd)


def is_running(name):
    """ returns a boolean indicating whether
    the site is config.running
    """
    cmd = "%s list sites /state:Started" % config.APP_CMD
    output = config.run(cmd)
    for line in output.splitlines():
        if line.split('"')[1] == name:
            return True
    return False


def stop(name):
    """ stops the site """
    if is_running(name):
        cmd = "%s stop site \"%s\"" % (config.APP_CMD, name)
        config.run(cmd)


def start(name):
    """ starts the site """
    if not is_running(name):
        cmd = "%s start site \"%s\"" % (config.APP_CMD, name)
        config.run(cmd)


def restart(name):
    """ restarts the site """
    stop(name)
    start(name)


def add_binding(name, protocol, port, ip='', host=''):
    """ adds a binding to an iis site
    Parameters:
    - name: site name
    - protocol: Examples: http, https, net.pipe, net.tcp,
        net.msmq, msmq.formatname, ftp
    - port: int - the port number
    - ip: the ip address - default = ''
    - host: the host assigned - default = ''
    """
    cmd = "%s set site %s /+bindings.[protocol='%s',bindingInformation='%s:%i:%s']"\
      % (config.APP_CMD, name, protocol, host, int(port), ip)
    config.run(cmd)


def remove_binding(name, protocol, port=None, ip='', host=''):
    """ remove one or more bindings from an iis site
    Parameters:
    - name: site name
    - protocol: Examples: http, https, net.pipe, net.tcp,
        net.msmq, msmq.formatname, ftp
    - port: optional int - the port number - default=None which mean any port
    - ip: the ip address - default = ''
    - host: the host assigned - default = ''
    """
    if port:
        cmd = "%s set site %s /-bindings.[protocol='%s',bindingInformation='%s:%i:%s']"\
          % (config.APP_CMD, name, protocol, host, int(port), ip)
    else:
        cmd = "%s set site %s /-bindings.[protocol='%s']"\
          % (config.APP_CMD, name, protocol)
    config.run(cmd)


def modify_binding(name, protocol, port, ip='', host=''):
    """ remove one or more bindings from an iis site
    Parameters:
    - name: site name
    - protocol: Examples: http, https, net.pipe, net.tcp,
        net.msmq, msmq.formatname, ftp
    - port: int - the port number
    - ip: the ip address - default = ''
    - host: the host assigned - default = ''
    """
    cmd = "%s set site %s /bindings.[protocol='%s',bindingInformation='%s:%i:%s']"\
      % (config.APP_CMD, name, protocol, host, int(port), ip)
    config.run(cmd)


def get_bindings(name):
    """ returns a list of bindings
    Parameters:
      name: site name
    """
    cmd = "%s list sites" % config.APP_CMD
    output = config.run(cmd, errMsg="You need elevated permissions.")
    for line in output.splitlines():
        parts = line.split('bindings:')
        if name in parts[0]:
            bindings = parts[1].split(',state')[0]
            return bindings.split(',')
    return []

