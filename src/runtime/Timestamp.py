
__all__ = ['now', 'parse']

from time import time, mktime, strptime

def now():
	return int(time() * 1000)

def parse(time_str):
	return int(1000 * mktime(strptime(time_str, "%Y-%m-%d %H:%M:%S")))
	

if __name__ == '__main__':
	print now()
	print parse('2008-11-13 11:22:11')

