import ctypes
from ctypes import *
#from ctypes import byref
#from ctypes import Structure, Union
from ctypes.wintypes import *

__author__ = 'Shao-chuan Wang'

LONGLONG = ctypes.c_longlong
HQUERY = HCOUNTER = HANDLE
pdh = ctypes.windll.pdh
Error_Success = 0x00000000
ERROR_SUCCESS = 0x00000000

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

class QueryCPUUsage:
    def __init__(self):
        self.hQuery = HQUERY()
        self.hCounter = HCOUNTER()
        if not pdh.PdhOpenQueryW(None,
                                 0,
                                 byref(self.hQuery)) == Error_Success:
            raise Exception
        if not pdh.PdhAddCounterW(self.hQuery,
                                 ur'\Processor(_Total)\% Processor Time',
                                 #ur'\Process(gvim)\% Processor Time',
                                 0,
                                 byref(self.hCounter)) == Error_Success:
            raise Exception

    def sample(self):
        if not pdh.PdhCollectQueryData(self.hQuery) == Error_Success:
            raise Exception

    def getCPUUsage(self):
        dwType = DWORD(0)
        value = PDH_FMT_COUNTERVALUE()
        if not pdh.PdhGetFormattedCounterValue(self.hCounter,
                                          PDH_FMT_LONG,
                                          byref(dwType),
                                          byref(value)) == Error_Success:
            raise Exception

        return value.union.longValue


####################################################################################################
def loopProcesses():
    NULL = 0
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
        raise RuntimeError("Second PdhEnumObjectItems failed with %0x%x" % status)

    print "Counters that the Process objects defines:\n"

    z = ''.join(pwsCounterListBuffer)
    counterList = z[:z.index('\x00\x00')].split('\x00')
    print counterList

    print "Instances of the Process object:\n"

    z = ''.join(pwsInstanceListBuffer)
    instanceList = z[:z.index('\x00\x00')].split('\x00')
    print instanceList

####################################################################################################

def testCPU():
    from time import sleep
    q = QueryCPUUsage()
    while(True):
        q.sample()
        sleep(1);
        print q.getCPUUsage()

if __name__=='__main__':
    #testCPU()
    loopProcesses()

