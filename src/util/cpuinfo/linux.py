

import platform
assert platform.uname()[0] == 'Linux', 'This module must be used under Linux'

__all__ = ['get_core_number', 'read_current_point', 'cpu_percentage_between_points',
           'get_pid_by_name', 'get_pids_by_name']

def get_core_number():
    fp = open('/proc/cpuinfo')
    lines = fp.readlines()
    fp.close()
    for line in lines:
        if line.startswith('cpu core'):
            return int(line[line.index(':')+1:])
    else:
        raise RuntimeError("Can't find cpu core information from /proc/cpuinfo")


def read_current_process_point(pid):
    try:
        statpath = '/proc/%d/stat' % pid
        fp = open(statpath)
    except IOError, e:
        raise RuntimeError('Open %s error because of %s.\nDoes process %d exist?' % (statpath, e, pid))
    lines = fp.readlines()
    fp.close()

    line = lines[0]
    values = line.split()

    assert int(values[0]) == int(pid)

    user    = int(values[13])
    system  = int(values[14])
    return user, system

def read_current_cpu_point():
    fp = open('/proc/stat')
    lines = fp.readlines()
    fp.close()

    line = lines[0]
    values = line.split()[1:]

    assert len(values) in (7, 8, 9), "%d fields" % len(values)

    user    = int(values[0])
    nice    = int(values[1])
    system  = int(values[2])
    idle    = int(values[3])
    iowait  = int(values[4])
    irq     = int(values[5])
    softirq = int(values[6])
    #???     = int(values[7]) # XXX: what does last item mean?

    return user, system, idle

def read_current_cpu_and_process_point(pid):
    return read_current_cpu_point() + read_current_process_point(pid)

def read_current_point(pid = None):
    if pid:
        return read_current_cpu_and_process_point(pid)
    else:
        return read_current_cpu_point()

def cpu_percentage_between_points(p1, p2):
    assert len(p1) == len(p2)
    if len(p1) == 3:
        user1, system1, idle1 = p1
        user2, system2, idle2 = p2
        u = user2 - user1
        s = system2 - system1
        i = idle2 - idle1
        return (u + s) * 100.0 / (u + s + i)
    else:
        assert len(p1) == 5
        user1, system1, idle1, puser1, psystem1 = p1
        user2, system2, idle2, puser2, psystem2 = p2
        u = user2 - user1
        s = system2 - system1
        i = idle2 - idle1
        pu = puser2 - puser1
        ps = psystem2 - psystem1
        return (pu + ps) * 100.0 / (u + s + i)

def get_pid_by_name(process):
    raise NotImplementedError()

def get_pids_by_name(process):
    raise NotImplementedError()

if __name__ == '__main__':
    print read_current_cpu_point()
    print read_current_process_point(3864)

# vim: expandtab:shiftwidth=4
