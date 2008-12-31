
import platform

if platform.uname()[0] == 'Linux':
	from linux import *
	__all__ = linux.__all__
elif platform.uname()[0] == 'Windows':
	from win import *
	__all__ = win.__all__
else:
	raise OSError('Supported platform %s' % platform.uname()[0])

