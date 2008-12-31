
import platform
assert platform.uname()[0] == 'Windows', 'This module must be used under Windows'

__all__ = ['get_core_number', 'CORE_NUMBER', 'read_current_cpu_point', 'cpu_percentage_between_points']

from ctypes import *
from ctypes.wintypes import *

##################################################

SystemBasicInformation       = 0
SystemPerformanceInformation = 2
SystemTimeInformation        = 3

PVOID = c_void_p
NULL = 0
NO_ERROR = 0

class SYSTEM_BASIC_INFORMATION(Structure):
	_fields_ = (('dwUnknown1', DWORD),
	            ('uKeMaximumIncrement', ULONG),
	            ('uPageSize', ULONG),
	            ('uMmNumberOfPhysicalPages', ULONG),
	            ('uMmLowestPhysicalPage', ULONG),
	            ('uMmHighestPhysicalPage', ULONG),
	            ('uAllocationGranularity', ULONG),
	            ('pLowestUserAddress', PVOID),
	            ('pMmHighestUserAddress', PVOID),
	            ('uKeActiveProcessors', ULONG),
	            ('bKeNumberProcessors', BYTE),
	            ('bUnknown2', BYTE),
	            ('wUnknown3', WORD),)

class SYSTEM_PERFORMANCE_INFORMATION(Structure):
	_fields_ = (('liIdleTime', LARGE_INTEGER),
	            ('dwSpare', ARRAY(DWORD, 76)),)

class SYSTEM_TIME_INFORMATION(Structure):
	_fields_ = (('liKeBootTime', LARGE_INTEGER),
	            ('liKeSystemTime', LARGE_INTEGER),
	            ('liExpTimeZoneBias', LARGE_INTEGER),
	            ('uCurrentTimeZoneId', ULONG),
	            ('dwReserved', DWORD),)

##################################################

# undocumented API!
# NtQuerySystemInformation(
#    IN UINT SystemInformationClass,    // information type
#    OUT PVOID SystemInformation,       // pointer to buffer
#    IN ULONG SystemInformationLength,  // buffer size in bytes
#    OUT PULONG ReturnLength OPTIONAL   // pointer to a 32-bit
#                                       // variable that receives
#                                       // the number of bytes
#                                       // written to the buffer 
# );
def NtQuerySystemInformation(SystemInformationClass,
                             SystemInformation,
                             SystemInformationLength,
                             OPTIONAL = NULL):
	status = windll.ntdll.NtQuerySystemInformation(SystemInformationClass,
	                                               SystemInformation,
	                                               SystemInformationLength,
	                                               OPTIONAL)
	if status != NO_ERROR:
		raise RuntimeError("WinAPI Error: NtQuerySystemInformation returned %s; GetLastError: %s" % (status, GetLastError()))

def SimpleNtQuerySystemInformation(SystemInformationClass, SystemInformation):
	NtQuerySystemInformation(SystemInformationClass,
                             pointer(SystemInformation),
                             sizeof(SystemInformation),
                             NULL)

##################################################

def get_core_number():
	SysBaseInfo = SYSTEM_BASIC_INFORMATION()
	SimpleNtQuerySystemInformation(SystemBasicInformation, SysBaseInfo)
	return SysBaseInfo.bKeNumberProcessors

CORE_NUMBER = get_core_number()

def Li2Double(x):
	return (x >> 32) * 4.294967296E9 + (x & 0xffffffff)

def read_current_cpu_point():
	SysTimeInfo = SYSTEM_TIME_INFORMATION()
	SysPerfInfo = SYSTEM_PERFORMANCE_INFORMATION()
	SimpleNtQuerySystemInformation(SystemTimeInformation, SysTimeInfo)
	SimpleNtQuerySystemInformation(SystemPerformanceInformation, SysPerfInfo)
	liOldSystemTime = SysTimeInfo.liKeSystemTime
	liOldIdleTime = SysPerfInfo.liIdleTime
	return Li2Double(liOldSystemTime), Li2Double(liOldIdleTime)


def cpu_percentage_between_points(p1, p2):
	liOldSystemTime, liOldIdleTime = p1
	liNewSystemTime, liNewIdleTime = p2

	# CurrentValue = NewValue - OldValue
	dbIdleTime = liNewIdleTime - liOldIdleTime
	dbSystemTime = liNewSystemTime - liOldSystemTime

	# CurrentCpuIdle = IdleTime / SystemTime
	dbIdleTime = dbIdleTime / dbSystemTime

	# CurrentCpuUsage% = 100 - (CurrentCpuIdle * 100) / NumberOfProcessors
	dbIdleTime = 100.0 - dbIdleTime * 100.0 / float(CORE_NUMBER) + 0.5 # XXX: why +0.5?

	return dbIdleTime

##################################################

def main():
	from time import sleep

	old_cpu_point = read_current_cpu_point()
	sleep(1)

	while True:
		new_cpu_point = read_current_cpu_point()
		usage_percentage = cpu_percentage_between_points(old_cpu_point,
		                                                 new_cpu_point)
		old_cpu_point = new_cpu_point

		print "%3d%%" % usage_percentage

		# wait one second
		sleep(1)

##################################################

if __name__ == '__main__':
	main()


