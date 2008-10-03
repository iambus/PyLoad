
class EmptyCoder:
	@classmethod
	def encode(cls, s):
		return s
	@classmethod
	def decode(cls, s):
		return s

class Rot13Coder:
	@classmethod
	def encode(cls, s):
		raise NotImplementedError()
	@classmethod
	def decode(cls, s):
		raise NotImplementedError()

class UnicodeCoder:
	@classmethod
	def encode(cls, s):
		raise NotImplementedError()
	@classmethod
	def decode(cls, s):
		raise NotImplementedError()


if __name__ == '__main__':
	print EmptyCoder.encode('x')
	print EmptyCoder.decode('x')
	en = EmptyCoder.encode
	print en('y')

