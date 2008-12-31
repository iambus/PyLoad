
import platform

osname = platform.uname()[0]

if osname == 'Linux':
	from linux import *
	__all__ = linux.__all__
elif osname == 'Windows':
	from win import *
	__all__ = win.__all__
else:
	raise OSError('Supported platform %s' % osname)

