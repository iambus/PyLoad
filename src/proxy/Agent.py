
PROCESS = None

import Settings

def fork():
	if not Settings.USE_AGENT:
		return
	global PROCESS
	assert PROCESS == None
	import subprocess
	PROCESS = subprocess.Popen(['python', '-c', 'import proxy.TwistedProxy as proxy; proxy.start_proxy()'], shell=False)
	# TODO: check return value
	return PROCESS

def fork_if():
	global PROCESS
	if PROCESS == None:
		fork()

def kill_command(pid):
	import sys
	return ({
		'linux2': 'kill %s',
		'win32': 'taskkill /F /PID %i',
	}[sys.platform] % pid).split()

def kill():
	if not Settings.USE_AGENT:
		return
	global PROCESS
	assert PROCESS != None
	import subprocess
	p = subprocess.Popen(kill_command(PROCESS.pid), shell=False)
	#p.wait()
	#PROCESS.wait()
	PROCESS = None
	# TODO: check return values

def kill_if():
	global PROCESS
	if PROCESS != None:
		kill()

if __name__ == '__main__':
	fork()

