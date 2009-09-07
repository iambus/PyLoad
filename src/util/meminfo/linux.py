
import platform
assert platform.uname()[0] == 'Linux', 'This module must be used under Linux'

__all__ = ['read_memory']


def read_memory(pid):
    ''' return [virtual memory, physical memory] '''
    assert type(pid) == int
    import os
    fp = os.popen('ps u -p %d --no-heading' % pid)
    try:
        memline = fp.read()
    finally:
        fp.close()
    return map(int, memline.split()[4:6])

