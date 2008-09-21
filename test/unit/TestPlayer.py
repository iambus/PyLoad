
import unittest
import LoadTestEnv

from Player import *
from Scope import *

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
		self.player.play()

		self.player.beforescript.script = 'i = 2'
		self.player.afterscript.script = 'i = i'
		self.player.play()

		self.player.p.beforescript.script = 'j = i'
		self.player.play()

		self.assertEqual(self.player.scope['i'], 2)
		self.assertEqual(self.player.p.scope.get_variables(), {})

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
		self.player.beforescript.script = 'r = 1'
		self.player.p.beforescript.script = 'p  = 1'
		self.player.p.h1.beforescript.script = 'h1 = 1'
		self.player.p.h2.beforescript.script = 'h2 = 1'

		self.player.play()

		self.assertEqual(sorted(self.player.scope.get_variables().keys()), ['__builtins__', 'r'])
		self.assertEqual(self.player.p.scope.get_variables(), {})
		self.assertEqual(self.player.p.h1.scope.get_variables(), {})
		self.assertEqual(self.player.p.h2.scope.get_variables(), {})

		self.player.p.h2.afterscript.script = 'h2 = k'
		self.assertRaises(NameError, self.player.play)


if __name__ == '__main__':
	unittest.main()


