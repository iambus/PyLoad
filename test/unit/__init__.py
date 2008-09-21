
import os

def main():
	import RunAllTests
	RunAllTests.main()

if os.path.isdir('unit'):
	os.chdir('unit')
	try:
		main()
	finally:
		os.chdir('..')
elif os.path.split(os.path.abspath('.'))[1] == 'unit':
	main()
else:
	raise 'You are running case in a wrong directory'

