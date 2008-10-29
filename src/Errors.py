
class Base(Exception):
	def __init__(self, message, traceback):
		Exception.__init__(self, message)
		self.traceback = traceback

class Error(Base):
	def __init__(self, message, traceback = None):
		Base.__init__(self, message, traceback)

	def rethrow(self):
		raise self, None, self.traceback

class ValidationError(Error):
	def __init__(self, message, traceback = None):
		Error.__init__(self, message, traceback)

##################################################

class ControlFlag(Base):
	def __init__(self, message = None, traceback = None):
		Base.__init__(self, message, traceback)

class TerminateRequest(ControlFlag):
	def __init__(self, message = None, traceback = None):
		Base.__init__(self, message, traceback)

class TerminateIteration(ControlFlag):
	def __init__(self, message = None, traceback = None):
		Base.__init__(self, message, traceback)

class TerminateUser(ControlFlag):
	def __init__(self, message = None, traceback = None):
		Base.__init__(self, message, traceback)

class TerminatePlaying(ControlFlag):
	def __init__(self, message = None, traceback = None):
		Base.__init__(self, message, traceback)



