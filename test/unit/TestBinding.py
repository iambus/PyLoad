
import unittest
import LoadTestEnv

from EditorPanel import Binding

class TestBinding(unittest.TestCase):

	def setUp(self):
		class C:
			def __init__(self):
				self.v = 7

		self.c = C()
		self.binding = Binding(self.c, 'v')

	def testBasic(self):
		self.assertEqual(self.c.v, 7)

		self.assertEqual(self.binding.get(), 7)

		self.binding.set(11)

		self.assertEqual(self.binding.get(), 11)


	def testGet(self):
		pass


if __name__ == '__main__':
	unittest.main()


