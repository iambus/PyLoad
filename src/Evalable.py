
import Scope

import Logger
log = Logger.getLogger()


class Evalable:
	def __init__(self):
		pass

	def execute(self):
		raise NotImplementedError()

	def eval(self):
		raise NotImplementedError()

class Script(Evalable):
	def __init__(self, script = '', scope = None):
		Evalable.__init__(self)
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


class Scoped(Evalable):
	def __init__(self, base = None):
		Evalable.__init__(self)
		self.scope = Scope.Scope(base)
		self.scripts = []
		self.childern = []

	def add_script(self, script):
		#script.scope = self.scope
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
		child.execute(Scope.Scope(base))

	def execute(self, base = None):
		if base == None:
			base = self.scope
		for script in self.scripts:
			script.execute(base)
		for child in self.childern:
			child.execute(Scope.Scope(base))

	def eval(self):
		raise NotImplementedError()



if __name__ == '__main__':
	scoped = Scoped()
	script1 = Script('print 1')
	script2 = Script('i = 77')
	script3 = Script('print i')
	scoped.add_script(script1)
	scoped.add_script(script2)
	scoped.add_script(script3)
	scoped.execute()


