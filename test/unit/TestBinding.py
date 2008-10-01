
import unittest
import LoadTestEnv

from Binding import *

class TestAttrBinding(unittest.TestCase):

	def setUp(self):
		class C:
			def __init__(self):
				self.v = 7

		self.c = C()
		self.binding = AttrBinding(self.c, 'v')

	def testBasic(self):
		self.assertEqual(self.c.v, 7)

		self.assertEqual(self.binding.get(), 7)

		self.binding.set(11)

		self.assertEqual(self.binding.get(), 11)

		self.assertEqual(self.c.v, 11)


	def testGet(self):
		pass

class TestFuncBinding(unittest.TestCase):
	def setUp(self):
		self.v = 5
		def read():
			return self.v
		def write(v):
			self.v = v
		self.binding = FuncBinding(read, write)

	def testBasic(self):
		self.assertEqual(self.v, 5)
		self.assertEqual(self.binding.get(), 5)
		self.binding.set(19)
		self.assertEqual(self.binding.get(), 19)
		self.assertEqual(self.v, 19)


if __name__ == '__main__':
	unittest.main()


