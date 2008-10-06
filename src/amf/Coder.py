
class SimpleAMFCoder:
	@classmethod
	def encode(cls, s):
		return eval(s)
	@classmethod
	def decode(cls, s):
		return repr(s)

