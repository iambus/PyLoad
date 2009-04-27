
import platform
assert platform.uname()[0] == 'Windows', 'This module must be used under Windows'

__all__ = ['read_memory']

from ctypes import *
from ctypes.wintypes import *

##################################################

NULL = 0

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

class LUID(Structure):
	_fields_ = (('LowPart', DWORD),
				('HighPart', LONG),)

class LUID_AND_ATTRIBUTES(Structure):
	_fields_ = (('Luid', LUID),
				('Attributes', ULONG),)

ANYSIZE_ARRAY = 1
class TOKEN_PRIVILEGES(Structure):
	_fields_ = (('PrivilegeCount', DWORD),
				('Privileges', LUID_AND_ATTRIBUTES * ANYSIZE_ARRAY),)


SE_PRIVILEGE_ENABLED_BY_DEFAULT = 0x00000001
SE_PRIVILEGE_ENABLED            = 0x00000002
SE_PRIVILEGE_USED_FOR_ACCESS    = 0x80000000

SE_CREATE_TOKEN_NAME              = "SeCreateTokenPrivilege"
SE_ASSIGNPRIMARYTOKEN_NAME        = "SeAssignPrimaryTokenPrivilege"
SE_LOCK_MEMORY_NAME               = "SeLockMemoryPrivilege"
SE_INCREASE_QUOTA_NAME            = "SeIncreaseQuotaPrivilege"
SE_UNSOLICITED_INPUT_NAME         = "SeUnsolicitedInputPrivilege"
SE_MACHINE_ACCOUNT_NAME           = "SeMachineAccountPrivilege"
SE_TCB_NAME                       = "SeTcbPrivilege"
SE_SECURITY_NAME                  = "SeSecurityPrivilege"
SE_TAKE_OWNERSHIP_NAME            = "SeTakeOwnershipPrivilege"
SE_LOAD_DRIVER_NAME               = "SeLoadDriverPrivilege"
SE_SYSTEM_PROFILE_NAME            = "SeSystemProfilePrivilege"
SE_SYSTEMTIME_NAME                = "SeSystemtimePrivilege"
SE_PROF_SINGLE_PROCESS_NAME       = "SeProfileSingleProcessPrivilege"
SE_INC_BASE_PRIORITY_NAME         = "SeIncreaseBasePriorityPrivilege"
SE_CREATE_PAGEFILE_NAME           = "SeCreatePagefilePrivilege"
SE_CREATE_PERMANENT_NAME          = "SeCreatePermanentPrivilege"
SE_BACKUP_NAME                    = "SeBackupPrivilege"
SE_RESTORE_NAME                   = "SeRestorePrivilege"
SE_SHUTDOWN_NAME                  = "SeShutdownPrivilege"
SE_DEBUG_NAME                     = "SeDebugPrivilege"
SE_AUDIT_NAME                     = "SeAuditPrivilege"
SE_SYSTEM_ENVIRONMENT_NAME        = "SeSystemEnvironmentPrivilege"
SE_CHANGE_NOTIFY_NAME             = "SeChangeNotifyPrivilege"
SE_REMOTE_SHUTDOWN_NAME           = "SeRemoteShutdownPrivilege"
SE_UNDOCK_NAME                    = "SeUndockPrivilege"
SE_SYNC_AGENT_NAME                = "SeSyncAgentPrivilege"
SE_ENABLE_DELEGATION_NAME         = "SeEnableDelegationPrivilege"
SE_MANAGE_VOLUME_NAME             = "SeManageVolumePrivilege"
SE_IMPERSONATE_NAME               = "SeImpersonatePrivilege"
SE_CREATE_GLOBAL_NAME             = "SeCreateGlobalPrivilege"


TOKEN_ASSIGN_PRIMARY    = 0x0001
TOKEN_DUPLICATE         = 0x0002
TOKEN_IMPERSONATE       = 0x0004
TOKEN_QUERY             = 0x0008
TOKEN_QUERY_SOURCE      = 0x0010
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_ADJUST_GROUPS     = 0x0040
TOKEN_ADJUST_DEFAULT    = 0x0080
TOKEN_ADJUST_SESSIONID  = 0x0100

def EnablePriv(lpszPriv):
	hToken = HANDLE()
	luid = LUID()
	tkprivs = TOKEN_PRIVILEGES()

#	windll.kernel32.ZeroMemory(byref(tkprivs), sizeof(tkprivs));
	
	if not windll.advapi32.OpenProcessToken(
		windll.kernel32.GetCurrentProcess(),
		(TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY),
		byref(hToken)):
		raise RuntimeError("WinAPI Error: OpenProcessToken")
		return False
	
	if not windll.advapi32.LookupPrivilegeValueA(NULL, lpszPriv, byref(luid)):
		CloseHandle(hToken)
		raise RuntimeError("WinAPI Error: LookupPrivilegeValueA")
		return False
	
	tkprivs.PrivilegeCount = 1
	tkprivs.Privileges[0].Luid = luid
	tkprivs.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
	
	bRet = windll.advapi32.AdjustTokenPrivileges(hToken, False, byref(tkprivs), sizeof(tkprivs), NULL, NULL)
	windll.kernel32.CloseHandle(hToken)
	return bRet

EnablePriv(SE_DEBUG_NAME)
EnablePriv(SE_INC_BASE_PRIORITY_NAME)

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
