
from struct import *
from AMFTypes import *


class AMFEncoder:
	def __init__(self, fp, packet):
		self.fp = fp
		self.packet = packet

		self.string_reference_table = []
		self.trait_reference_table = []
		self.complex_object_reference_table = []

		self.string_rref_table = {}
		self.trait_rref_table = {}
		self.complex_rref_table = {}

	def decode(self):
		pass

	########################################
	# {{{ write basic types

	def write_byte(self, b):
		#assert type(b) == int
		return self.fp.write(chr(b))

	def write_u16(self, i):
		return self.fp.write(pack('>h', i))

	def write_u32(self, i):
		return self.fp.write(pack('>i', i))

	def write_u29(self, i):
		# assert (i & 0xe0000000) == 0
		if i < 0:
			i = 0x20000000 + i
		if (i & 0x1fff80) == 0:
			b1 = i
			self.write_byte(b1)
		elif (i & 0x1fffc000) == 0:
			b1 = (i >> 7) | 0x80
			b2 = i & 0x7f
			self.write_byte(b1)
			self.write_byte(b2)
		elif (i & 0x1fe00000) == 0:
			b1 = (i >> 14) | 0x80
			b2 = ((i >> 7) & 0x7f) | 0x80
			b3 = i & 0x7f
			self.write_byte(b1)
			self.write_byte(b2)
			self.write_byte(b3)
		else:
			b1 = (i >> 21) | 0x80
			b2 = ((i >> 14) & 0x7f) | 0x80
			b3 = ((i >> 7) & 0x7f) | 0x80
			b4 = i & 0xff
			self.write_byte(b1)
			self.write_byte(b2)
			self.write_byte(b3)
			self.write_byte(b4)

	def write_utf8(self, s):
		utf8 = s.encode('utf-8')
		self.write_u16(len(utf8))
		self.fp.write(utf8)

	def write_utf8_long(self, s):
		utf8 = s.encode('utf-8')
		self.write_u32(len(utf8))
		self.fp.write(utf8)

	def write_utf8_vr(self, s):
		if s == '':
			self.fp.write('0x01')
			return
		utf8 = s.encode('utf-8')
		index = self.string_rref_table.get(utf8)
		if index != None:
			u = index << 1
			self.write_u29(u)
		else:
			u = (len(utf-8) << 1) | 1
			self.write_u29(u)
			self.fp.write(utf-8)

			index = len(self.string_reference_table)
			self.string_reference_table.append(utf-8)
			self.string_rref_table[utf-8] = index

	def write_null(self):
		pass

	def write_false(self):
		pass

	def write_true(self):
		pass

	def write_double(self, d):
		self.fp.write(pack('!d', d))
	# }}}
	########################################










# vim: foldmethod=marker:
