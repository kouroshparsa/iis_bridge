"""
    This module is used for manipulating iis sites
    :copyright: (c) 2014 by Kourosh Parsa.
"""
from iis_bridge.config import *
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
    cmd = "%s list sites" % APP_CMD
    output = run(cmd)
    return "/*:%s:," % port in output


def get_port(site_name):
    """ Given the iis site name
    it returns the port number of the site - integer
    """
    cmd = "%s list sites|findstr \"%s\"" % (APP_CMD, site_name)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, err = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError("The site [%s] does not exist. %s"\
            % (site_name, err))
    port = output.split(":")[3]
    return int(port)


def get_url(site_name):
    """ Given the iis site name
    it returns the site url
    """
    cmd = "%s list sites|findstr \"%s\"" % (APP_CMD, site_name)
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
    cmd = "%s list sites" % APP_CMD
    output = run(cmd)
    for line in output.splitlines():
        if line.split('"')[1] == name:
            return True
    return False


def create(name, port, path, pool_name, protocol="http", site_id=None):
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
    cmd = "%s add site /name:\"%s\" /physicalPath:\"%s\" /bindings:%s/*:%i:"\
          % (APP_CMD, name, path, protocol, port)
    if site_id:
        cmd = "%s /id:%i" % (cmd, site_id)
    run(cmd)
    run("%s set app \"%s/\" /applicationPool:\"%s\""\
        % (APP_CMD, name, pool_name))
    for iter in range(5):# wait a bit
        if exists(name):
            break
        time.sleep(1)


def delete(name):
    """ deletes a site given its name """
    if not exists(name):
        print("The site '%s' does not exist." % name)
        return

    cmd = "%s delete site \"%s\"" % (APP_CMD, name)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    proc.wait()


def is_running(name):
    """ returns a boolean indicating whether
    the site is running
    """
    cmd = "%s list sites /state:Started" % APP_CMD
    output = run(cmd)
    for line in output.splitlines():
        if line.split('"')[1] == name:
            return True
    return False


def stop(name):
    """ stops the site """
    if is_running(name):
        cmd = "%s stop site \"%s\"" % (APP_CMD, name)
        run(cmd)


def start(name):
    """ starts the site """
    if not is_running(name):
        cmd = "%s start site \"%s\"" % (APP_CMD, name)
        run(cmd)


def restart(name):
    """ restarts the site """
    stop(name)
    start(name)


