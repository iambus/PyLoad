
import unittest
import LoadTestEnv

from Player import Script
from PlayPolicy import *
from Scope import Scope

class TestIteration(unittest.TestCase):
	def setUp(self):
		self.player = Script()
		self.it = Iteration(self.player)
	
	def testBasic(self):
		self.it.beforescript.script = 'i = 0'
		self.player.script = 'j = i'
		self.it.play()

	def testAddon(self):
		self.it.beforescript.script = 'i = 0'
		self.player.script = 'j = i'
		self.it.play(Scope())

	def testScope1(self):
		self.player.script = 'j = k'
		self.assertRaises(NameError, self.it.play)

	def testScope2(self):
		self.it.beforescript.script = 'i = k'
		self.assertRaises(NameError, self.it.play)

class TestUser(unittest.TestCase):
	def setUp(self):
		self.it_factory = IterationFactory()
		self.player = Script()
		self.scope = Scope()

		self.it_factory.beforescript.script = 'i = i + 1'
		self.user = User(self.player, 2, self.it_factory)
		self.user.beforescript.script = 'i = 0'
		self.user.afterscript.script = 'assert i == 2'

	def testBasic(self):
		self.user.play()

	def testAddon(self):
		self.user.play(self.scope)
	
	def testScope(self):
		self.it_factory.beforescript.script = 'i = i + 1'
		user = User(self.player, 2, self.it_factory)
		user.beforescript.script = 'i = 0'
		user.afterscript.script = 'j = k'
		self.assertRaises(NameError, user.play)


class TestIterationBasedPlayPolicy(unittest.TestCase):
	def setUp(self):
		self.global_factory = GlobalFactory()
		self.user_factory = UserFactory()
		self.iteration_factory = IterationFactory()
	
	def testBasic(self):
		self.global_factory.beforescript.script = 'i = 2'
		self.user_factory.beforescript.script = 'j = i'
		self.iteration_factory.beforescript.script = 'k = j'
		player = Script('assert i == k')
		policy = IterationBasedPlayPolicy(player, 2, 3,
				self.user_factory, self.iteration_factory, self.global_factory)
		policy.play()

	def testScope(self):
		player = Script('assert i == k')
		policy = IterationBasedPlayPolicy(player, 2, 3,
				self.user_factory, self.iteration_factory, self.global_factory)
		self.assertRaises(NameError, policy.play_in_single_thread)

if __name__ == '__main__':
	unittest.main()

