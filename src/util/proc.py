

from cpuinfo import read_current_point, cpu_percentage_between_points, get_pid_by_name
from cpu import CPUBox
from meminfo import read_memory

class Process:
	def __init__(self, pid):
		if type(pid) == int:
			pass
		elif isinstance(pid, basestring):
			pid = get_pid_by_name(pid)
		else:
			raise RuntimeError("Argument must be integer or string")
		self.pid = pid
		self.cpu = CPUBox(pid)

	def get_memories(self):
		virtual_memory, phisical_memory = read_memory(self.pid)
		return virtual_memory, phisical_memory

	def get_cpu(self):
		return self.cpu.get_cpu()

	def get_process_path(self):
		raise NotImplementedError()

class SystemProcess:
	def __init__(self):
		self.cpu = CPUBox()
	def get_cpu(self):
		return self.cpu.get_cpu()

