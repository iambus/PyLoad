
import unittest

import LoadTestEnv

import Scope

class TestScope(unittest.TestCase):

	def setUp(self):
		self.base = Scope.Scope()
		self.scope = Scope.Scope(self.base)

		self.base.assign('x1', 1)
		self.base['x2'] = 2
		self.scope.assign('y1', 11)
		self.scope['y2'] = 12

	def testBasic(self):
		self.assertEqual(self.scope.base, self.base)

		self.assertEqual(self.base['x1'], 1)
		self.assertEqual(self.base.lookup('x2'), 2)
		self.assertEqual(self.scope['y1'], 11)
		self.assertEqual(self.scope.lookup('y2'), 12)

		self.assertEqual(self.base.variables, {'x1':1, 'x2':2})
		self.assertEqual(self.scope.variables, {'y1':11, 'y2':12})

		self.base['x3'] = 3
		self.scope['x3'] = 3

		self.assertEqual(self.base.variables, {'x1':1, 'x2':2, 'x3':3})
		self.assertEqual(self.scope.variables, {'y1':11, 'y2':12})

	def testGetVariables(self):
		self.assertEqual(self.base.get_variables(), {'x1':1, 'x2':2})
		self.assertEqual(self.scope.get_variables(), {'x1':1, 'x2':2, "y1":11, "y2":12})

	def testEval(self):
		self.assertEquals(self.scope.eval('3'), 3)
		self.assertEquals(self.scope.eval('x1'), 1)
		self.assertEquals(self.scope.eval('y1'), 11)
		self.assertEquals(self.scope.eval('askfjlafjkj'), None)
		self.assertRaises(SyntaxError, lambda:self.scope.eval('@#$@$$'))

		self.scope.execute('x1=0;i=0;j=i;k=x2;y2=k')
		self.assertEqual(self.base['x1'], 0)
		self.assertEqual(self.base['i'], None)
		self.assertEqual(self.scope['i'], 0)
		self.assertEqual(self.scope['j'], 0)
		self.assertEqual(self.scope['k'], 2)
		self.assertEqual(self.scope['y2'], 2)

	def testGlobal(self):
		script = '''
def f():
	global x2
	x1 = 0
	x2 = 1
f()
assert x1 == 1
x1 = 2
y2 = -1
'''
		self.scope.execute(script)
		self.assertEqual(self.base['x1'], 2)
		self.assertEqual(self.base['x2'], 1)
		self.assertEqual(self.base['y2'], None)
		self.assertEqual(self.scope['y2'], -1)

class TestLife(unittest.TestCase):
	def setUp(self):
		self.life = Scope.Life()

	def testBase(self):
		self.assertEqual(self.life.eval('2'), 2)
		self.life.execute('i=2;j=3;k=5')
		# Now:
		# i = 2, j = 3, k = 5
		self.assertEqual(self.life['i'], 2)

		scope = Scope.Scope()
		scope['x'] = 77
		scope['j'] = 88
		self.life.push(scope)
		# Now:
		# i = 2, j = 3, k = 5
		# x = 77, j = 88
		self.assertEqual(self.life['x'], 77)
		self.assertEqual(self.life.eval('x'), 77)
		self.assertEqual(self.life['i'], 2)
		self.assertEqual(self.life['j'], 88)
		self.life.execute('i=100;j=100')
		# Now:
		# i = 100, j = 3, k = 5
		# x = 77, j = 100
		self.life.pop()
		# Now:
		# i = 100, j = 3, k = 5
		self.assertEqual(self.life['x'], None)
		self.assertEqual(self.life.eval('x'), None)
		self.assertEqual(self.life['i'], 100)
		self.assertEqual(self.life['j'], 3)
		self.assertEqual(self.life['k'], 5)

		s1 = Scope.Scope()
		s1['x'] = 2
		s2 = Scope.Scope()
		s2['y'] = 3
		self.life.push(s1)
		self.life.push(s2)
		self.life['x'] = 3
		self.life['z'] = 5
		self.assertEqual(s1['x'], 3)
		self.assertEqual(s2['z'], 5)


if __name__ == '__main__':
	unittest.main()


