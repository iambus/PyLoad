
from Player import *

##################################################
class ControlFlag(Exception):
	pass

class Break(ControlFlag):
	pass

##################################################
class Controller:
	pass

class Group(Player, Controller):
	def __init__(self):
		pass

class If(Player, Controller):
	def __init__(self, condition = 'True'):
		Player.__init__(self)
		assert type(condition) == str or type(condition) == unicode
		self.condition = Script(condition)

	def playmain(self, basescope):
		if self.condition.eval(basescope):
			Player.playmain(self, basescope)

class Loop(Player, Controller):
	def __init__(self, condition = 'True'):
		Player.__init__(self)
		assert type(condition) == str or type(condition) == unicode
		self.condition = Script(condition)

	def playmain(self, basescope):
		while self.condition.eval(basescope):
			try:
				Player.playmain(self, basescope)
			except Break:
				break

if __name__ == '__main__':
	import Globals
	g = Globals.copy_globals()
	g['Break'] = Break

	loop = Loop('x < 5')
	loop.scope.variables = g
	loop.add_script(Script('x += 1'))
	loop.add_script(Script('print x'))
	loop.add_script(Script('if x == 2: raise Break()'))
	loop.beforescript = Script('x = 0')
	loop.afterscript = Script('print "===end==="')
	loop.play()


