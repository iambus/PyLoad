
import unittest
import LoadTestEnv

from Player import *
from Scope import *

#TODO: please rewrite it since the implementation was changed.

##################################################
# test old Evalable class Script (now in Player)
class TestScript(unittest.TestCase):

	def setUp(self):
		self.script = Script()

	def testBasic(self):
		self.script.execute()

		self.script.script = 'i = 2'
		self.script.execute()

		# script has no local variables
		self.script.script = 'j = i'
		self.assertRaises(NameError, self.script.execute)

		scope = Scope()
		scope['k'] = 3
		self.script.script = 'i = k; assert i == 3'
		self.script.execute(scope)

		self.script.script = 'j = i'
		self.assertRaises(NameError, self.script.execute)

		scope = Scope()
		self.script.script = 'j = i'
		self.assertRaises(NameError, lambda:self.script.execute(scope))

	def testConstructor(self):
		scope = Scope()
		script = Script('i = 2')
		script.execute(scope)
		script.script = 'j = i'
		script.execute(scope)

		script = Script('i = k')
		self.assertRaises(NameError, script.execute)

	def testEval(self):
		self.script.script = '2'
		self.assertEqual(self.script.eval(), 2)

##################################################

class B(Player):
	def __init__(self):
		Player.__init__(self)
		self.script = Script('')

	def play(self, base):
		self.script.execute(base)

class D(Player):
	def __init__(self):
		Player.__init__(self)
		self.childern = [B(), B(), B()]
		self.script = Script('')
	
	def play(self, base = None):
		if base == None:
			base = Scope()
		self.script.execute(base)
		Player.play(self, base)


# test old Evalable class Scoped (merged into Player)
class TestScoped(unittest.TestCase):

	def setUp(self):
		self.scoped = D()

	def testBasic(self):
		self.scoped.script.script = 'i = 2'
		self.scoped.childern[0].script.script = 'j = i'
		self.scoped.childern[1].script.script = 'j = i'
		self.scoped.play()

		self.scoped.childern[2].script.script = 'k = kk'
		self.assertRaises(NameError, self.scoped.play)

		self.scoped.script.script = 'x = i'
		self.assertRaises(NameError, self.scoped.play)

		self.scoped.script.script = 'x = j'
		self.assertRaises(NameError, self.scoped.play)

	def testScope(self):
		scope = Scope()
		scope['x'] = 9
		self.scoped.script.script = 'i = x'
		self.scoped.play(scope)
		self.assertEqual(scope['i'], 9)

	def testExecuteScript(self):
		scope = Scope()

		self.scoped.script.script = 'i = 2'
		self.scoped.play(scope)

		script = Script('j = i')
		self.scoped.execute_script(script, scope)

		script = Script('j = k')
		self.assertRaises(NameError, lambda:self.scoped.execute_script(script, scope))

		scope = Scope()
		scope['k'] = 3
		self.scoped.execute_script(script, scope)
		self.assertEqual(scope['j'], 3)

	def testExecuteChild(self):
		scope = Scope()
		self.scoped.script.script = 'i = 2'
		script = Script('j = 3')
		self.scoped.execute_child(script, scope)
		self.assertEquals(scope.get_names(), [])

		script = Script('j = k')
		self.assertRaises(NameError, lambda:self.scoped.execute_script(script))

		scope = Scope()
		scope['x'] = 11
		self.scoped.execute_child(Script('j = x; x = 22'), scope)
		self.assertEquals(scope.get_names(), ['x'])
		self.assertEquals(scope['x'], 22)

		self.assertRaises(NameError, lambda:self.scoped.execute_child(Script('j = k'), scope))

##################################################

class H(Player):
	def __init__(self):
		Player.__init__(self)

class P(Player):
	def __init__(self):
		Player.__init__(self)
		self.h1 = H()
		self.h2 = H()
		self.childern = [self.h1, self.h2]

class R(Player):
	def __init__(self):
		Player.__init__(self)
		self.p = P()
		self.childern.append(self.p)

class TestPlayer(unittest.TestCase):

	def setUp(self):
		self.player = R()

	def testBasic(self):
		scope = Scope()

		self.player.play(scope)

		self.player.beforescript.script = 'i = 2'
		self.player.afterscript.script = 'i = i'
		self.player.play(scope)

		self.player.p.beforescript.script = 'j = i'
		self.player.play(scope)

		self.assertEqual(scope['i'], 2)

		self.player.afterscript.script = 'i = j'
		self.assertRaises(NameError, self.player.play)

	def testNone(self):
		self.player.play()

	def testBefore(self):
		self.player.beforescript.script = 'i = 2'
		self.player.before()

		self.player.beforescript.script = 'i = 2 ; j = k'
		self.assertRaises(NameError, self.player.before)

		scope = Scope()
		scope['k'] = 2
		self.player.before(scope)

	def testPage(self):
		self.player.p.beforescript.script = 'j = 3'
		self.player.p.h1.beforescript.script = 'k = j'
		self.player.play()

		self.player.p.beforescript.script = ''
		self.player.p.h1.beforescript.script = 'k = j'

		self.assertRaises(NameError, self.player.play)

	def testLocal(self):
		scope = Scope()

		self.player.beforescript.script = 'r = 1'
		self.player.p.beforescript.script = 'p  = 1'
		self.player.p.h1.beforescript.script = 'h1 = 1'
		self.player.p.h2.beforescript.script = 'h2 = 1'

		self.player.play(scope)

		self.assertEqual(sorted(scope.get_variables().keys()), ['__builtins__', 'r'])

		self.player.p.h2.afterscript.script = 'h2 = k'
		self.assertRaises(NameError, self.player.play)

##################################################

if __name__ == '__main__':
	unittest.main()


