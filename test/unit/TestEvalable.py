
import unittest
import LoadTestEnv

from Evalable import *
from Scope import *


##################################################

class TestEvalable(unittest.TestCase):

	def setUp(self):
		pass

	def testBasic(self):
		pass

##################################################

class TestScript(unittest.TestCase):

	def setUp(self):
		self.script = Script()

	def testBasic(self):
		self.script.execute()

		self.script.script = 'i = 2'
		self.script.execute()

		# i is local variable in script
		self.script.script = 'j = i'
		self.script.execute()

		self.script.script = 'i = k'
		self.assertRaises(NameError, self.script.execute)

		scope = Scope()
		scope['k'] = 3
		self.script.script = 'i = k; assert i == 3'
		self.script.execute(scope)

		self.script.script = 'j = i'
		self.script.execute()

		scope = Scope()
		self.script.script = 'j = i'
		self.assertRaises(NameError, lambda:self.script.execute(scope))

	def testConstructor(self):
		script = Script('i = 2')
		script.execute()
		script.script = 'j = i'
		script.execute()

		script = Script('i = k')
		self.assertRaises(NameError, script.execute)

##################################################

class B(Scoped):
	def __init__(self):
		Scoped.__init__(self)
		self.script = Script('')

	def execute(self, base):
		self.script.execute(base)

class D(Scoped):
	def __init__(self):
		Scoped.__init__(self)
		self.childern = [B(), B(), B()]
		self.script = Script('')
	
	def execute(self, base = None):
		if base == None:
			base = self.scope
		self.script.execute(base)
		Scoped.execute(self, base)


class TestScoped(unittest.TestCase):

	def setUp(self):
		self.scoped = D()

	def testBasic(self):
		self.scoped.script.script = 'i = 2'
		self.scoped.childern[0].script.script = 'j = i'
		self.scoped.childern[1].script.script = 'j = i'
		self.scoped.execute()

		self.scoped.childern[2].script.script = 'k = kk'
		self.assertRaises(NameError, self.scoped.execute)

		self.scoped.script.script = 'x = i'
		self.assertRaises(NameError, self.scoped.execute)

		self.scoped.script.script = 'x = j'
		self.assertRaises(NameError, self.scoped.execute)

	def testScope(self):
		scope = Scope()
		scope['x'] = 9
		self.scoped.script.script = 'i = x'
		self.scoped.execute(scope)
		self.assertEqual(scope['i'], 9)
		self.assertEqual(self.scoped.scope['i'], None)

	def testExecuteScript(self):
		self.scoped.script.script = 'i = 2'
		self.scoped.execute()

		script = Script('j = i')
		self.scoped.execute_script(script)

		script = Script('j = k')
		self.assertRaises(NameError, lambda:self.scoped.execute_script(script))

		scope = Scope()
		scope['k'] = 3
		self.scoped.execute_script(script, scope)
		self.assertEqual(scope['j'], 3)

	def testExecuteChild(self):
		self.scoped.script.script = 'i = 2'
		script = Script('j = 3')
		self.scoped.execute_child(script)
		self.assertEquals(self.scoped.scope.get_names(), [])

		script = Script('j = k')
		self.assertRaises(NameError, lambda:self.scoped.execute_script(script))

		scope = Scope()
		scope['x'] = 11
		self.scoped.execute_child(Script('j = x; x = 22'), scope)
		self.assertEquals(self.scoped.scope.get_names(), [])
		self.assertEquals(scope.get_names(), ['x'])
		self.assertEquals(scope['x'], 22)

		self.assertRaises(NameError, lambda:self.scoped.execute_child(Script('j = k'), scope))


##################################################

if __name__ == '__main__':
	unittest.main()


