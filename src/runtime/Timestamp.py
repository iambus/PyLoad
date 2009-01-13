
__all__ = ['now', 'parse', 'format']

from time import time, mktime, strptime, localtime, strftime

TIME_STR_FORMAT = "%Y-%m-%d %H:%M:%S"

def now():
	return int(time() * 1000)

def parse(time_str):
	return int(1000 * mktime(strptime(time_str, TIME_STR_FORMAT)))
	
def format(t):
	return strftime(TIME_STR_FORMAT, localtime(t/1000.0))

if __name__ == '__main__':
	print now()
	print parse('2008-11-13 11:22:11')
	print format(now())

	n = now()
	assert parse(format(n)) == n - n % 1000

