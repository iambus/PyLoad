
from Playable import Playable
import Scope

class Script(Playable):
	def __init__(self, script = '', scope = None):
		Playable.__init__(self)
		self.script = script
		self.scope = scope

	def execute(self, scope = None):
		if scope == None:
			if self.scope == None:
				self.scope = Scope.Scope()
			scope = self.scope
		scope.execute(self.script)

	def eval(self, scope = None):
		if scope == None:
			if self.scope == None:
				self.scope = Scope.Scope()
			scope = self.scope
		return scope.eval(self.script)

	def play(self, scope = None):
		self.execute(scope)

class Player(Playable):
	def __init__(self):
		Playable.__init__(self)

		self.scope = Scope.Scope()
		self.scripts = []
		self.childern = []

		self.beforescript = Script('')
		self.afterscript = Script('')

	def add_script(self, script):
		assert isinstance(script, Script)
		self.scripts.append(script)
	
	def add_child(self, child):
		assert isinstance(child, Playable)
		self.childern.append(child)

	def remove_script(self, script):
		assert isinstance(script, Script) or isinstance(script, str) or isinstance(script, unicode)
		if isinstance(script, Script):
			uuid = script.uuid
		else:
			uuid = script

		for s in self.scripts:
			if s.uuid == uuid:
				self.scripts.remove(s)
				assert uuid == script or s == script, 'Two different scripts own the same uuid?'
				break

	def remove_child(self, child):
		assert isinstance(child, Playable) or isinstance(script, str) or isinstance(script, unicode)
		if isinstance(child, Playable):
			uuid = child.uuid
		else:
			uuid = child

		for c in self.childern:
			if c.uuid == uuid:
				self.childern.remove(c)
				assert uuid == child or c == child, 'Two different objs own the same uuid?'
				break

	
	def execute_script(self, script, base = None):
		assert isinstance(script, Script)
		if base == None:
			base = self.scope
		script.execute(base)

	#TODO: give a better name
	def execute_here(self, child, scope = None):
		assert isinstance(child, Playable)
		if scope == None:
			scope = self.scope
		child.play(scope)

	def execute_child(self, child, base = None):
		assert isinstance(child, Playable)
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


