
import unittest
import LoadTestEnv

from Controller import *
from Scope import Scope

#TODO: please rewrite it since the implementation was changed.

class TestIf(unittest.TestCase):
	def setUp(self):
		self.If = If('i == 5')
		self.If.beforescript = Script('i = 5')
		self.If.add_child(Script('i = 2'))
		self.If.afterscript = Script('assert i == 2')
	
	def testBasic(self):
		self.If.play()
	
	def testChildScope(self):
		self.If = If('True')
		self.If.add_child(Script('i = 2'))
		self.If.afterscript = Script('assert i == 2')
		self.assertRaises(NameError, self.If.play)

	def testScriptScope(self):
		self.If = If('True')
		self.If.add_script(Script('i = 2'))
		self.If.afterscript = Script('assert i == 2')
		self.If.play()

	def testException(self):
		self.If = If('x == 5')
		self.If.play()

	def testGlobalVariables(self):
		scope = Scope()
		scope['i'] = 1
		self.If = If('i')
		self.If.add_child(Script('j = i'))
		self.If.add_child(Script('i = 0'))
		self.If.afterscript = Script('assert i == 0')
		self.If.play(Scope(scope))
		self.assertEquals(scope['i'], 0)

class TestLoop(unittest.TestCase):
	def setUp(self):
		self.loop = Loop('x < 10')
		self.loop.beforescript = Script('x = 0;y = 0')
		self.loop.add_script(Script('x += 1'))
		self.loop.add_script(Script('y += 1'))
		self.loop.afterscript = Script('assert x >= 10; assert y == 10')

	def testBasic(self):
		scope = Scope()
		self.loop.play(scope)

		self.assertEqual(scope.lookup('x'), 10)
		self.assertEqual(scope.lookup('y'), 10)
	
	def testChild(self):
		self.loop = Loop('x < 10')
		self.loop.beforescript = Script('x = 0;y = 0')
		self.loop.add_child(Script('x += 1'))
		self.loop.add_child(Script('y += 1'))
		self.loop.afterscript = Script('assert x >= 10; assert y == 10')
		self.loop.play()

	def testBreak(self):
		import Globals
		g = Globals.copy_globals()
		g['Break'] = Break

		scope = Scope()
		scope.variables = g
		self.loop.add_script(Script('if y == 3: raise Break()'))
		self.loop.afterscript = Script('assert x == 3; assert y == 3')
		self.loop.play(scope)
		self.assertEqual(scope.lookup('x'), 3)
		self.assertEqual(scope.lookup('y'), 3)


class TestBreak(unittest.TestCase):
	def setUp(self):
		pass


if __name__ == '__main__':
	unittest.main()

