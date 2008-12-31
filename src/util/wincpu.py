
from ctypes import *
from ctypes.wintypes import *

# undocumented API!
NtQuerySystemInformation = windll.ntdll.NtQuerySystemInformation

SystemBasicInformation       = 0
SystemPerformanceInformation = 2
SystemTimeInformation        = 3

Li2Double = lambda x: float(x >> 32) * 4.294967296E9 + float(x & 0xffffffff)

PVOID = c_void_p

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


def main():
	SysPerfInfo = SYSTEM_PERFORMANCE_INFORMATION()
	SysTimeInfo = SYSTEM_TIME_INFORMATION()
	SysBaseInfo = SYSTEM_BASIC_INFORMATION()
	dbIdleTime = DOUBLE()
	dbSystemTime = DOUBLE()
	status = LONG()
	#liOldIdleTime = LARGE_INTEGER(0)
	liOldIdleTime = 0L
	liOldSystemTime = LARGE_INTEGER(0)

	NULL = c_void_p()
	#NULL = 0
	NO_ERROR = 0
	# get number of processors in the system
	status = NtQuerySystemInformation(SystemBasicInformation, pointer(SysBaseInfo), sizeof(SysBaseInfo), NULL)
	if status != NO_ERROR:
		return

	#while not _kbhit():
	while True:
		# get new system time
		status = NtQuerySystemInformation(SystemTimeInformation, pointer(SysTimeInfo), sizeof(SysTimeInfo), 0)
		if status!=NO_ERROR:
			raise RuntimeError( "WinAPI Error: %s" % GetLastError() )

		# get new CPU's idle time
		status = NtQuerySystemInformation(SystemPerformanceInformation, pointer(SysPerfInfo), sizeof(SysPerfInfo), NULL)
		if status != NO_ERROR:
			raise RuntimeError( "WinAPI Error: %s" % GetLastError() )

		# if it's a first call - skip it
		if liOldIdleTime != 0:
			# CurrentValue = NewValue - OldValue
			dbIdleTime = Li2Double(SysPerfInfo.liIdleTime) - Li2Double(liOldIdleTime)
			dbSystemTime = Li2Double(SysTimeInfo.liKeSystemTime) - Li2Double(liOldSystemTime)

			# CurrentCpuIdle = IdleTime / SystemTime
			dbIdleTime = dbIdleTime / dbSystemTime

			# CurrentCpuUsage% = 100 - (CurrentCpuIdle * 100) / NumberOfProcessors
			dbIdleTime = 100.0 - dbIdleTime * 100.0 / float(SysBaseInfo.bKeNumberProcessors) + 0.5

			print "%3d%%" % dbIdleTime

		# store new CPU's idle and system time
		liOldIdleTime = SysPerfInfo.liIdleTime
		liOldSystemTime = SysTimeInfo.liKeSystemTime

		# wait one second
		from time import sleep
		sleep(1)
	print

if __name__ == '__main__':
	main()


