
import os
import glob

import unittest

def warning():
	marked = ['__init__.py', 'RunAllTests.py', 'LoadTestEnv.py']
	goodpatterns = ['Test*.py', '*.pyc', '*.log', '*.bat']
	files = [i for j in map(glob.glob, goodpatterns) for i in j] + marked
	files = set(files)
	allfiles = set(glob.glob('*'))
	x = allfiles.difference(files)
	if x:
		print 'WARNING: Ignored items:', list(x)
		print


def buildTestSuite():
	suite = unittest.TestSuite()
	for filename in glob.glob('Test*.py'):
		modulename = os.path.splitext(filename)[0]
		modulesuite = unittest.defaultTestLoader.loadTestsFromName(modulename)
		suite.addTest(modulesuite)
	return suite

def main():
	warning()
	results = unittest.TextTestRunner().run(buildTestSuite())
	assert results.wasSuccessful(), 'Unit tests fail!'

if __name__ == '__main__':
	main()

