
class AttrBinding:
	def __init__(self, variable, name):
		self.variable = variable
		self.name = name
	def get(self):
		return getattr(self.variable, self.name)
	def set(self, value):
		setattr(self.variable, self.name, value)

class FuncBinding:
	def __init__(self, readfunc, writefunc):
		self.readfunc = readfunc
		self.writefunc = writefunc
	def get(self):
		return self.readfunc()
	def set(self, value):
		self.writefunc(value)

class ConstBinding:
	def __init__(self, value):
		self.value = value

	def get(self):
		return self.value


