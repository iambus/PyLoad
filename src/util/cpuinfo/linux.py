

import platform
assert platform.uname()[0] == 'Linux', 'This module must be used under Linux'

__ALL__ = ['get_core_number', 'read_current_cpu_point', 'cpu_percentage_between_points']

def get_core_number():
    fp = open('/proc/cpuinfo')
    lines = fp.readlines()
    fp.close()
    for line in lines:
        if line.startswith('cpu core'):
            return int(line[line.index(':')+1:])
    else:
        raise RuntimeError("Can't find cpu core information from /proc/cpuinfo")


def read_current_cpu_point():
    fp = open('/proc/stat')
    lines = fp.readlines()
    fp.close()

    line = lines[0]
    values = line.split()[1:]

    assert len(values) == 7 or len(values) == 8

    user    = int(values[0])
    nice    = int(values[1])
    system  = int(values[2])
    idle    = int(values[3])
    iowait  = int(values[4])
    irq     = int(values[5])
    softirq = int(values[6])

    return user, system, idle


def cpu_percentage_between_points(p1, p2):
    user1, system1, idle1 = p1
    user2, system2, idle2 = p2
    u = user2 - user1
    s = system2 - system1
    i = idle2 - idle1
    return (u + s) * 100.0 / (u + s + i)


# vim: expandtab:shiftwidth=4
