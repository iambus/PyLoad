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
	def __init__(self):
		self.encoding = 'ascii'

	@classmethod
	def encode(cls, s):
		if type(s) == str:
			encodings = ['ascii', 'utf-8', 'gbk']
			for encoding in encodings:
				try:
					s = s.decode(encoding)
				except UnicodeDecodeError:
					continue
				else:
					break
		return s

	@classmethod
	def decode(cls, s):
		if type(s) == unicode:
			encodings = ['ascii', 'utf-8', 'gbk']
			for encoding in encodings:
				try:
					s = s.encode(encoding)
				except UnicodeEncodeError:
					continue
				else:
					break
		return s

# TODO
class GZipCoder:
	pass

from amf.Coder import SimpleAMFCoder as AMFCoder

if __name__ == '__main__':
	print EmptyCoder.encode('x')
	print EmptyCoder.decode('x')
	en = EmptyCoder.encode
	print en('y')

