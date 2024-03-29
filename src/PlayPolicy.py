
from Scope import Scope
from Player import Player, Script
import Repository

import Errors

import Logger
log = Logger.getLogger()

class Iteration(Player):
	def __init__(self, player = None):
		Player.__init__(self)
		self.player = player
	def play(self, scope = None):
		assert self.scripts == [] and self.children == []
		self.children = [self.player]
		try:
			Player.play(self, scope)
		except Errors.TerminateIteration, e:
			log.exception('Iteration terminated because of %s' % e)
		self.children = []

class User(Player):
	def __init__(self, player = None, iteration_count = 1, iteration_factory = None):
		Player.__init__(self)
		self.player = player
		self.iteration_count = iteration_count
		self.iteration_factory = iteration_factory
		self.user_index = -1

	def play(self, scope = None):
		scope = Scope(scope)
		scope['_USER_INDEX_'] = self.user_index
		assert self.scripts == [] and self.children == []
		global_reporter = scope.lookup('global_reporter')
		if global_reporter:
			reporter = global_reporter.get_reporter()
			scope['reporter'] = reporter
		else:
			reporter = None
		try:
			if self.iteration_factory:
				self.before(scope)
				for i in range(self.iteration_count):
					# TODO: put _ITERATION_INDEX_ in iteration scope instead of user scope
					scope['_ITERATION_INDEX_'] = i
					iteration = self.iteration_factory.create()
					iteration.player = self.player
					Player.execute_here(self, iteration, scope)
				self.after(scope)
			else:
				try:
					for i in range(self.iteration_count):
						scope['_ITERATION_INDEX_'] = i
						self.children.append(self.player)
					Player.play(self, scope)
				finally:
					self.children = []
		except Errors.TerminateUser, e:
			log.exception('User terminated because of %s' % e)
		if reporter:
			reporter.commit()

class Global(Player):
	def __init__(self):
		Player.__init__(self)
	def before(self, scope):
		Player.before(self, scope)
	def play(self, scope):
		Player.play(self, scope)
	def after(self, scope):
		Player.after(self, scope)


class Factory(Repository.Mixin):
	def __init__(self, C):
		Repository.Mixin.__init__(self)
		self.C = C
		self.beforescript = Script('')
		self.afterscript = Script('')

	def create(self):
		player = self.C()
		player.beforescript.script = self.beforescript.script
		player.afterscript.script = self.afterscript.script
		return player

	def test_play(self):
		scope = Scope()
		self.beforescript.execute(scope)
		self.afterscript.execute(scope)


def UserFactory():
	return Factory(User)

def IterationFactory():
	return Factory(Iteration)

def GlobalFactory():
	return Factory(Global)


import threading
class UserThread(threading.Thread):
	def __init__(self, user):
		threading.Thread.__init__(self, name='UserThread')
		self.user = user

	def run(self):
		try:
			self.user.play(self.scope)
		except Exception, e:
			import traceback, sys
			traceback.print_tb( sys.exc_info()[2] )
			print e
			# just print it right now
			# TODO: notify main thread

	def play(self, scope):
		self.scope = scope
		self.start()

class TimeBasedPlayPolicy:
	def __init__(self):
		raise NotImplementedError('Time Based Policy is not supported now.')

class IterationBasedPlayPolicy:
	def __init__(self, player, user_count, iteration_count, user_factory, iteration_factory, global_factory, reporter = None):
		self.player = player
		self.user_count = user_count
		self.iteration_count = iteration_count
		self.user_factory = user_factory
		self.iteration_factory = iteration_factory
		self.global_factory = global_factory

		self.reporter = reporter

	def play_in_single_thread(self, scope = None):
		g = self.global_factory.create()
		users = []
		scope = Scope(scope)
		scope['_USER_COUNT_'] = self.user_count
		scope['_ITERATION_COUNT_'] = self.iteration_count
		scope['_PLAYER_'] = self.player
		if self.reporter:
			scope['global_reporter'] = self.reporter
		g.before(scope)
		for i in range(self.user_count):
			user = self.user_factory.create()
			user.player = self.player
			user.iteration_count = self.iteration_count
			user.iteration_factory = self.iteration_factory
			user.user_index = i
			users.append(user)
			user.play(scope)
		g.after(scope)

	def play_in_multiple_threads(self, scope = None):
		g = self.global_factory.create()
		users = []
		scope = Scope(scope)
		scope['_USER_COUNT_'] = self.user_count
		scope['_ITERATION_COUNT_'] = self.iteration_count
		scope['_PLAYER_'] = self.player
		if self.reporter:
			scope['global_reporter'] = self.reporter
		g.before(scope)
		for i in range(self.user_count):
			user = self.user_factory.create()
			user.player = self.player
			user.iteration_count = self.iteration_count
			user.iteration_factory = self.iteration_factory
			user.user_index = i
			user = UserThread(user)
			users.append(user)
			user.play(scope)
		for user in users:
			user.join()
		g.after(scope)

	play = play_in_multiple_threads

if __name__ == '__main__':
	pass

