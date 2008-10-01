
import Playable
import Scope

class Script():
	def __init__(self, script = '', scope = None):
		self.script = script
		self.scope = scope

	def execute(self, scope = None):
		if scope == None:
			if self.scope == None:
				self.scope = Scope.Scope()
			scope = self.scope
		scope.execute(self.script)

	def eval(self):
		raise NotImplementedError()

	def play(self, scope):
		self.execute(scope)

class Player(Playable.Playable):
	def __init__(self):
		Playable.Playable.__init__(self)

		self.scope = Scope.Scope()
		self.scripts = []
		self.childern = []

		self.beforescript = Script('')
		self.afterscript = Script('')

	def add_script(self, script):
		self.scripts.append(script)
	
	def add_childern(self, child):
		childern.append(child)
	
	def execute_script(self, script, base = None):
		if base == None:
			base = self.scope
		script.execute(base)

	def execute_child(self, child, base = None):
		if base == None:
			base = self.scope
		child.play(Scope.Scope(base))

	def play(self, basescope = None):
		if basescope == None:
			basescope = self.scope
		self.before(basescope)
		self.playmain(basescope)
		self.after(basescope)

	def before(self, basescope = None):
		self.execute_script(self.beforescript, basescope)

	def playmain(self, basescope):
		for script in self.scripts:
			script.execute(basescope)
		for child in self.childern:
			child.play(Scope.Scope(basescope))

	def after(self, basescope = None):
		self.execute_script(self.afterscript, basescope)


class Controller:
	pass


if __name__ == '__main__':
	player = Player()
	player.beforescript = Script('print "before"')
	player.afterscript = Script('print "after"')
	player.play()

	scoped = Player()
	script1 = Script('print 1')
	script2 = Script('i = 77')
	script3 = Script('print i')
	scoped.add_script(script1)
	scoped.add_script(script2)
	scoped.add_script(script3)
	scoped.play()


