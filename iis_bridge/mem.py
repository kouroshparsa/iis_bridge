"""
    This module retrieves iis worker memory
    :copyright: (c) 2014 by Kourosh Parsa.
"""
import iis_bridge.config as config
import subprocess
MEM_TYPES = ['WorkingSetPrivate', 'WorkingSetSize']

class Worker():
    """ this class represents an iis worker object"""
    def __init__(self, poolname=None, pid=None,\
        mem_type=MEM_TYPES[0], mem=None):
        self.poolname = poolname
        self.pid = int(pid)
        self.mem = float(mem)
        self.mem_type = mem_type
    def __str__(self):
        return "%s: pid=%i %s=%i" %\
               (self.poolname, self.pid, self.mem_type, self.mem)


def get_mem(pid, mem_type=MEM_TYPES[0], mem_unit='KB'):
    """ given the process id and the type of memory
    this method retrieves the memory usage in bytes
    and returns it as an integer
    """
    if mem_type == MEM_TYPES[0]:
        cmd = "%s path Win32_PerfRawData_PerfProc_Process get IDProcess,WorkingSetPrivate"\
          % config.WMIC
    elif mem_type == MEM_TYPES[1]:
        cmd = "%s path win32_process get ProcessId,WorkingSetSize"\
              % config.WMIC
    else:
        raise Exception("Invalid memory type: %s" % mem_type)

    output = config.run(cmd)
    for line in output.splitlines():
        line = line.strip()
        ind = line.find(' ')
        if ind > 0:
            pidstr = line[0:ind].strip()
            if pidstr.isdigit() and\
                pid == int(pidstr):
                mem = int(line[ind+1:].strip())
                if mem_unit == 'KB':
                    mem /= 1024.0
                if mem_unit == 'MB':
                    mem = mem / 1024.0 / 1024.0
                return mem
    raise Exception('The pid was not  found: %i' % pid)


def get_workers(mem_type=MEM_TYPES[0], mem_unit='KB'):
    """ returns a list of Worker objects
    """
    workers = []
    cmd = "sc query w3svc"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    if not "RUNNING" in output:
        config.run("sc start w3svc")
    cmd = "%s list wps" % config.APP_CMD
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    if proc.returncode != 0:
        if "ERROR" in output:
            raise Exception("Either the WAS service is down or "\
                "You need elevated permissions.")
        else:
            return []

    for line in output.splitlines():
        if len(line) > 5:
            pid = int(line.split('"')[1])
            worker = Worker(poolname=line[line.find(':')+1:-1],\
                    pid=pid,\
                    mem=get_mem(pid, mem_type, mem_unit),\
                    mem_type=mem_type)
            workers.append(worker)
    return workers


if __name__ == "__main__":
    print [str(w) for w in get_workers()]
