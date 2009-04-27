
import platform
assert platform.uname()[0] == 'Windows', 'This module must be used under Windows'

__all__ = ['read_memory']

from ctypes import *
from ctypes.wintypes import *

##################################################


PROCESS_QUERY_INFORMATION = 0x0400L
PROCESS_VM_READ           = 0x0010L

class PROCESS_MEMORY_COUNTERS(Structure):
	_fields_ = (('cb', DWORD),
				('PageFaultCount', DWORD),
				('PeakWorkingSetSize', c_size_t),
				('WorkingSetSize', c_size_t),
				('QuotaPeakPagedPoolUsage', c_size_t),
				('QuotaPagedPoolUsage', c_size_t),
				('QuotaPeakNonPagedPoolUsage', c_size_t),
				('QuotaNonPagedPoolUsage', c_size_t),
				('PagefileUsage', c_size_t),
				('PeakPagefileUsage', c_size_t),)

def SimpleOpenProcess(processID):
	hProcess = windll.kernel32.OpenProcess( PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, processID )
	if not hProcess:
		raise RuntimeError("WinAPI Error: OpenProcess failed; GetLastError: %s" % (GetLastError()))
	return hProcess

def SimpleCloseProcess(hProcess):
	windll.kernel32.CloseHandle( hProcess )

def GetProcessMemoryInfo(Process, ppsmemCounters, cb):
	status = windll.psapi.GetProcessMemoryInfo( Process, ppsmemCounters, cb)
	if not status:
		raise RuntimeError("WinAPI Error: GetProcessMemoryInfo returned %s; GetLastError: %s" % (status, GetLastError()))

def SimpleGetProcessMemoryInfo(Process, psmemCounters):
	GetProcessMemoryInfo(Process, byref(psmemCounters), sizeof(psmemCounters))

def ReadMemoryInfo( processID ):
	print processID
	pmc = PROCESS_MEMORY_COUNTERS()
	hProcess = SimpleOpenProcess( processID )
	try:
		SimpleGetProcessMemoryInfo( hProcess, pmc)
		for attr in dir(pmc):
			if not attr.startswith('_'):
				print attr, getattr(pmc, attr)
		return 0
	finally:
		SimpleCloseProcess( hProcess )


def read_memory(pid):
	assert type(pid) == int
	return ReadMemoryInfo(pid)
