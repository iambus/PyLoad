

import copy

class Scope:
	def __init__(self, base = None):
		self.base = base
		self.variables = {}

	def __getitem__(self, key):
		return self.lookup(key)

	def __setitem__(self, key, val):
		self.assign(key, val)

	def lookup(self, name):
		assert type(name) == str or type(name) == unicode
		if self.variables.has_key(name):
			return self.variables[name]
		elif self.base:
			return self.base.lookup(name)
		return None
	
	def assign(self, name, value = None):
		assert type(name) == str or type(name) == unicode
		if self.assign_existed(name, value):
			return
		elif self.base and self.base.assign_existed(name, value):
			return
		else:
			self.variables[name] = value

	def assign_existed(self, name, value):
		if self.variables.has_key(name):
			self.variables[name] = value
			return True
		else:
			return False

	def get_variables(self):
		if not self.base:
			return copy.copy(self.variables)
		else:
			d = self.base.get_variables()
			d.update(self.variables)
			return d
	
	# For debug usage, don't return built names
	def get_names(self):
		names = self.get_variables().keys()
		names.sort()
		if '__builtins__' in names:
			names.remove('__builtins__')
		return names

	def execute(self, script):
		variables = self.get_variables()
		exec script in variables
		for k, v in variables.items():
			self[k] = v

	def eval(self, script):
		try:
			return eval(script, self.get_variables())
		except NameError:
			return None

	def clear(self):
		self.variables.clear()

class Life:
	def __init__(self):
		self.scopes = []
		self.scopes.append(Scope())

	def __getitem__(self, key):
		return self.scopes[-1][key]

	def __setitem__(self, key, val):
		self.scopes[-1][key] = val

	def push(self, scope = None):
		if scope == None:
			scope = Scope()
		assert scope.base == None, 'Scope overloaded...'
		scope.base = self.scopes[-1]
		self.scopes.append(scope)
	
	def pop(self):
		assert len(self.scopes) > 1, "Can't pop top scope"
		return self.scopes.pop()

	def execute(self, script):
		assert len(self.scopes) >= 1
		self.scopes[-1].execute(script)

	def eval(self, script):
		assert len(self.scopes) >= 1
		return self.scopes[-1].eval(script)




if __name__ == '__main__':
	s1 = Scope()
	s1.assign('x', 1)
	s1.assign('x2', 2)
	s2 = Scope(s1)
	s2.assign('y', 4)
	print s2.lookup('x')

