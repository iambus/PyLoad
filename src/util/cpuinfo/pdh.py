
__all__ = []

import ctypes
from ctypes import *
from ctypes.wintypes import *


LONGLONG = ctypes.c_longlong
HQUERY = HCOUNTER = HANDLE
pdh = ctypes.windll.pdh
Error_Success = 0x00000000
ERROR_SUCCESS = 0x00000000

NULL = 0
PDH_FMT_LONG = 0x00000100

class PDH_Counter_Union(Union):
    _fields_ = [('longValue', LONG),
                ('doubleValue', ctypes.c_double),
                ('largeValue', LONGLONG),
                ('AnsiStringValue', LPCSTR),
                ('WideStringValue', LPCWSTR)]

class PDH_FMT_COUNTERVALUE(Structure):
    _fields_ = [('CStatus', DWORD),
                ('union', PDH_Counter_Union),]

##################################################

def PdhCollectQueryData(query):
    status = pdh.PdhCollectQueryData(query)
    if status != Error_Success:
        raise RuntimeError('PdhCollectQueryData returns %s(0x%x)' % (status, 0xFFFFFFFF&status))
    return status


def PdhOpenQuery(query):
    status = pdh.PdhOpenQueryW(None,
                             0,
                             byref(query))
    if status != Error_Success:
        raise RuntimeError('PdhOpenQuery returns %s(0x%x)' % (status, 0xFFFFFFFF&status))
    return status

def PdhCloseQuery(query):
    pdh.PdhCloseQuery(query)

def PdhAddCounter(query, counterPath, counter):
    status = pdh.PdhAddCounterW(query, counterPath, 0, byref(counter))
    if status != Error_Success:
        raise RuntimeError('PdhAddCounter returns %s(0x%x)' % (status, 0xFFFFFFFF&status))
    return status

def PdhGetFormattedCounterValue(counter, format, value):
    status = pdh.PdhGetFormattedCounterValue(counter, format, 0, byref(value))
    if status != Error_Success:
        raise RuntimeError('PdhGetFormattedCounterValue returns %s(0x%x)' % (status, 0xFFFFFFFF&status))
    return status

##################################################
def getProcessInstances():
    PERF_DETAIL_WIZARD = 400
    PDH_MORE_DATA = DWORD(0x800007D2L)
    COUNTER_OBJECT = u'Process'

    pwsCounterListBuffer = LPWSTR(NULL)
    dwCounterListSize = DWORD(0)
    pwsInstanceListBuffer = LPWSTR(NULL)
    dwInstanceListSize = DWORD(0)
    pTemp = LPWSTR(NULL)

    # Determine the required buffer size for the data.
    status = pdh.PdhEnumObjectItemsW(
        NULL,                   # real-time source
        NULL,                   # local machine
        COUNTER_OBJECT,         # object to enumerate
        NULL,                   # pass NULL and 0
        pointer(dwCounterListSize),     # to get required buffer size
        pwsInstanceListBuffer,
        pointer(dwInstanceListSize),
        PERF_DETAIL_WIZARD,     # counter detail level
        0)
    status = DWORD(status)

    if status.value != PDH_MORE_DATA.value:
        raise RuntimeError("PdhEnumObjectItems failed with %d (0x%x|0x%x)" % (status, status, 0xFFFFFFFFL & status))

    # Allocate the buffers and try the call again.
    pwsCounterListBuffer = ARRAY(WCHAR, dwCounterListSize.value)()
    pwsInstanceListBuffer = ARRAY(WCHAR, dwInstanceListSize.value)()

    status = pdh.PdhEnumObjectItemsW(
       NULL,                   # real-time source
       NULL,                   # local machine
       COUNTER_OBJECT,         # object to enumerate
       pointer(pwsCounterListBuffer),
       pointer(dwCounterListSize),
       pwsInstanceListBuffer,
       pointer(dwInstanceListSize),
       PERF_DETAIL_WIZARD,     # counter detail level
       0)

    if status != ERROR_SUCCESS:
        raise RuntimeError("Second PdhEnumObjectItems failed with 0x%x" % status)

    z = ''.join(pwsCounterListBuffer)
    counterList = z[:z.index('\x00\x00')].split('\x00')

    z = ''.join(pwsInstanceListBuffer)
    instanceList = z[:z.index('\x00\x00')].split('\x00')
    instanceList = [i.lower() for i in instanceList]
    return instanceList

def getInstancePID(instance):
    hQuery = HQUERY()
    hCounter = HCOUNTER()
    PdhOpenQuery(hQuery)
    PdhAddCounter(hQuery,
                 ur'\Process(%s)\ID Process' % instance,
                 hCounter)

    PdhCollectQueryData(hQuery)

    dwType = DWORD(0)
    value = PDH_FMT_COUNTERVALUE()
    PdhGetFormattedCounterValue(hCounter, PDH_FMT_LONG, value)
    PdhCloseQuery(hQuery)

    return value.union.longValue

def getProcessInstance(pid):
    processes = set()
    for p in getProcessInstances():
        if p not in processes:
            processes.add(p)
        else:
            n = 1
            while '%s#%d' % (p, n) in processes:
                n += 1
            processes.add('%s#%d' % (p, n))
    for p in processes:
        if getInstancePID(p) == pid:
            return p
    raise RuntimeError("No process with pid %d" % pid)

##################################################
class QueryCPUUsage:
    def __init__(self, process = None):
        if isinstance(process, int):
            process = getProcessInstance(process)
        self.process = process
        if process:
            self.counterPath = ur'\Process(%s)\%% Processor Time' % process
        else:
            self.counterPath = ur'\Processor(_Total)\% Processor Time'

        self.hQuery = HQUERY()
        self.hCounter = HCOUNTER()
        PdhOpenQuery(self.hQuery)
        PdhAddCounter(self.hQuery,
                       self.counterPath,
                       self.hCounter)

        self.sample()

    def sample(self):
        PdhCollectQueryData(self.hQuery)

    def getCPUUsage(self):
        value = PDH_FMT_COUNTERVALUE()
        PdhGetFormattedCounterValue(self.hCounter, PDH_FMT_LONG, value)

        return value.union.longValue

    def close(self):
        PdhCloseQuery(self.hQuery)

def GetPIDByName(process):
    process = process.lower()
    processes = getProcessInstances()
    n = processes.count(process)
    if n > 2:
        raise RuntimeError("Don't know which %s pid to get. There are %d." % (process, n))
    if n == 0:
        raise RuntimeError("No %s found" % process)
    return getInstancePID(process)

def GetPIDsByName(process):
    process = process.lower()
    processes = getProcessInstances()
    n = processes.count(process)
    if n == 0:
        return []
    if n == 1:
        return [getInstancePID(process)]
    return map(getInstancePID, ['%s#%d' % (process, i) for i in range(n)])

##################################################

def testCPU():
    from time import sleep
    q = QueryCPUUsage('FIREFOX')
    while(True):
        q.sample()
        sleep(1);
        print q.getCPUUsage()

if __name__=='__main__':
    testCPU()

