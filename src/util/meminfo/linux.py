
import platform
assert platform.uname()[0] == 'Linux', 'This module must be used under Linux'

__all__ = ['read_memory']


def read_memory(pid):
	assert type(pid) == int
	raise NotImplementedError()

