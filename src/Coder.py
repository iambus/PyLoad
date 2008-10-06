"""

decode:
	convert raw request/response to human readable format
encode:
	convert human readable format to request/response

"""

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

from amf.Coder import SimpleAMFCoder as AMFCoder

if __name__ == '__main__':
	print EmptyCoder.encode('x')
	print EmptyCoder.decode('x')
	en = EmptyCoder.encode
	print en('y')

