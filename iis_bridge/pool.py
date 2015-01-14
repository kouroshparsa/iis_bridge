"""
    This module is used for manipulating iis pools
    :copyright: (c) 2014 by Kourosh Parsa.
"""
from iis_bridge.config import *
import time
IDENTITIES = ["ApplicationPoolIdentity", "LocalService", "LocalSystem", "NetworkService", "SpecificUser"]
    
def exists(name):
    """ given the pool name, returns whether
    the pool already exists
    """
    cmd = "%s list apppool" % APP_CMD
    output = run(cmd)
    for line in output.splitlines():
        if line.split('"')[1] == name:
            return True
    return False


def create(name, runtime_version="4.0", pipeline_mode="Integrated"):
    """ creates a new iis pool
    Parameters:
    - name: pool name
    - runtime_version: .Net framework version
    - pipeline_mode: Integrated, Classic
    """
    if exists(name):
        print("The pool '%s' already exists." % name)
        return

    cmd = "%s add apppool /name:\"%s\"" % (APP_CMD, name)
    if runtime_version:
        cmd = "%s /managedRuntimeVersion:v%s" % (cmd, runtime_version)

    if pipeline_mode not in PIPELINE_MODES:
        raise Exception("Invalid pipeline mode: %s" % pipeline_mode)

    cmd = "%s /managedPipelineMode:%s" % (cmd, pipeline_mode)
    run(cmd)
    time.sleep(1) # some appcmd commands fail without this delay


def config(name, private_mem=None, max_proc=None, thirty_two_bit=None,\
           recycle_after_time=None, recycle_at_time=None,\
           runtime_version=None, idle_timeout=None,\
           identity=None, username=None, password=None,\
           pipeline_mode=None, loadUserProfile=None,
           ping_enabled=None, ping_period=None, ping_response_time=None):

    """ configures the app pool
    Parameters:
    - name: pool name
    - private_mem: private memory limit in KB
    - max_proc: maximum number of worker processes
    - thirty_two_bit: boolean, whether to enable 32bit support
    - recycle_after_time: pool recycle time interval (in minutes)
    - recycle_at_time: the specific time to recycle the pool
    - runtime_version: .Net framework version
    - idle_timeout: timeout of pool workers being idle in minutes
    - identity: type of identity pool
    - username: username for specific user
    - password: password for specific user
    - pipeline_mode: Integrated, Classic
    - loadUserProfile: boolean - whether to load user profile
    - ping_enabled: boolean - whether to enable ping
    - ping_period: in seconds
    - ping_response_time: ping response timeout in seconds
    """
    if private_mem:
        cmd = "%s set config /section:applicationPools \"/[name='%s'].recycling.periodicRestart.privateMemory:%s\""\
          % (APP_CMD, name, private_mem)
        run(cmd)

    if max_proc:
        cmd = "%s set apppool \"%s\" -processModel.maxProcesses:%s\""\
          % (APP_CMD, name, max_proc)
        run(cmd)

    if thirty_two_bit != None:
        cmd = "%s set apppool \"/apppool.name:%s\" /enable32BitAppOnWin64:%s"\
              % (APP_CMD, name, str(thirty_two_bit))
        run(cmd)

    if recycle_after_time:
        cmd = "%s set apppool \"/apppool.name:%s\" /recycling.periodicRestart.time:%s"\
              % (APP_CMD, name, str(recycle_after_time))
        run(cmd)
        
    if recycle_at_time:
        cmd = "%s set apppool \"/apppool.name:%s\" /-recycling.periodicRestart.schedule"\
              % (APP_CMD, name)
        run(cmd)

        cmd = "%s set apppool \"/apppool.name:%s\" /+recycling.periodicRestart.schedule.[value='%s']"\
              % (APP_CMD, name, str(recycle_at_time))
        run(cmd)

    if runtime_version:
        cmd = "%s set apppool \"/apppool.name:%s\" /managedRuntimeVersion:v%s"\
              % (APP_CMD, name, str(runtime_version))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        proc.wait()

    if idle_timeout:
        cmd = "%s set config /section:applicationPools \"/[name='%s'].processModel.idleTimeout:%s\""\
              % (APP_CMD, name, str(idle_timeout))
        run(cmd)

    if identity:
        if identity not in IDENTITIES:
            raise Exception("Invalid Identity: %s. "\
                "Choose from:" % (identity, IDENTITIES))
        if identity == "SpecificUser":
            if not (username and password):
                raise Exception("Please specify a username "\
                    "and a password for specific user.")

            cmd = "%s set config /section:applicationPools" \
                    " \"/[name='%s'].processModel.identityType:SpecificUser\""\
                    " \"/[name='%s'].processModel.userName:%s\""\
                    " \"/[name='%s'].processModel.password:%s"\
                     % (APP_CMD, name, name, username, name, password)
            run(cmd)
        else:
            cmd = "%s set config /section:applicationPools" \
                    " \"/[name='%s'].processModel.identityType:%s\""\
                     % (APP_CMD, name, identity)
            run(cmd)

    if loadUserProfile != None:
        cmd = "%s set config /section:applicationPools \"/[name='%s'].ProcessModel.loadUserProfile:%s\""\
          % (APP_CMD, name, str(loadUserProfile))
        run(cmd)

    if pipeline_mode:
        if pipeline_mode not in PIPELINE_MODES:
            raise Exception("Invalid pipeline mode: %s" % pipeline_mode)
        cmd = "%s set config /section:applicationPools \"/[name='%s'].ProcessModel.pipelineMode:%s\""\
          % (APP_CMD, name, pipeline_mode)
        run(cmd)

    if ping_enabled != None:
        cmd = "%s set config /section:applicationPools \"/[name='%s'].ProcessModel.pingingEnabled:%s\""\
          % (APP_CMD, name, str(ping_enabled))
        run(cmd)

    if ping_period != None:
        ping_period = str(ping_period)
        if ":" not in ping_period:
            ping_period = "00:00:%s" % ping_period
        cmd = "%s set config /section:applicationPools \"/[name='%s'].ProcessModel.PingInterval:%s\""\
          % (APP_CMD, name, ping_period)
        run(cmd)

    if ping_response_time:
        ping_response_time = str(ping_response_time)
        if ":" not in ping_response_time:
            ping_response_time = "00:00:%s" % ping_response_time
        cmd = "%s set config /section:applicationPools \"/[name='%s'].ProcessModel.pingResponseTime:%s\""\
          % (APP_CMD, name, ping_response_time)
        run(cmd)


def delete(name):
    """ deletes a pool given its name """
    if not exists(name):
        print("The pool '%s' does not exist." % name)
        return

    cmd = "%s delete apppool \"%s\"" % (APP_CMD, name)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    proc.wait()


def is_running(name):
    """ returns a boolean indicating whether
    the pool is running
    """
    cmd = "%s list apppools /state:Started" % APP_CMD
    output = run(cmd)
    for line in output.splitlines():
        if line.split('"')[1] == name:
            return True
    return False


def stop(name):
    """ stops the pool """
    if is_running(name):
        cmd = "%s stop apppool \"%s\"" % (APP_CMD, name)
        run(cmd)


def start(name):
    """ starts the pool """
    if not is_running(name):
        cmd = "%s start apppool \"%s\"" % (APP_CMD, name)
        run(cmd)


def restart(name):
    """ restarts the pool """
    stop(name)
    start(name)

