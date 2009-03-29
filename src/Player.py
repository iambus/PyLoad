
from Playable import Playable
from Scope import Scope

class Script(Playable):
	def __init__(self, script = ''):
		Playable.__init__(self)
		self.script = script

	def execute(self, scope = None):
		if scope == None:
			scope = Scope()
		scope.execute(self.script)

	def eval(self, scope = None):
		if scope == None:
			scope = Scope()
		return scope.eval(self.script)

	def play(self, scope = None):
		self.execute(scope)

class Player(Playable):
	def __init__(self):
		Playable.__init__(self)

		self.scripts = []
		self.children = []

		self.beforescript = Script('')
		self.afterscript = Script('')

	def add_script(self, script):
		assert isinstance(script, Script)
		self.scripts.append(script)
	
	def add_child(self, child):
		assert isinstance(child, Playable)
		self.children.append(child)

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

	def remove_child(self, child, index = -1):
		assert isinstance(child, Playable) or isinstance(script, str) or isinstance(script, unicode)
		if isinstance(child, Playable):
			uuid = child.uuid
		else:
			uuid = child

		if index != -1:
			c = self.children[index]
			assert c.uuid == uuid
			self.children.pop(-1)
		else:
			for c in self.children:
				if c.uuid == uuid:
					self.children.remove(c)
					assert child == uuid or child == c, 'Two different objs own the same uuid?'
					break

	
	def execute_script(self, script, base = None):
		assert isinstance(script, Script)
		if base == None:
			base = Scope()
		script.execute(base)

	#TODO: give a better name
	def execute_here(self, child, scope = None):
		assert isinstance(child, Playable)
		if scope == None:
			scope = Scope()
		child.play(scope)

	def execute_child(self, child, base = None):
		assert isinstance(child, Playable)
		if base == None:
			base = Scope()
		child.play(Scope(base))

	def play(self, basescope = None):
		if basescope == None:
			basescope = Scope()
		self.before(basescope)
		self.playmain(basescope)
		self.after(basescope)

	def before(self, basescope = None):
		self.execute_script(self.beforescript, basescope)

	def playmain(self, basescope):
		for script in self.scripts:
			script.execute(basescope)
		for child in self.children:
			child.play(Scope(basescope))

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


