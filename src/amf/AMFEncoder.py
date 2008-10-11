
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
		packet = self.packet
		assert packet.version == 3, 'Only AMF 3 is supported'
		self.write_u16(packet.version)

		self.write_u16(len(packet.headers))

		for header in packet.headers:
			self.write_utf8(header.header_name)
			self.write_byte(int(header.must_understand))
			self.write_u32(-1)
			self.write_value(header.value)
			self.switch_to_amf0()

		self.write_u16(len(packet.messages))
		for message in packet.messages:
			self.write_utf8(message.target_uri)
			self.write_utf8(message.response_uri)
			self.write_u32(-1)
			self.write_value(header.value)
			self.switch_to_amf0()


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
	# {{{ write arrays and objects

	def write_strict_array(self, array):
		array = array.array
		array_count = self.read_u32()
		self.write_u32(len(array))
		array = []
		for i in array:
			self.write_value(i)

	def write_array(self, array):
		pass

	def write_object(self, obj):
		pass

	# }}}
	########################################
	def write_value0(self, value):
		if isinstance(value, AMF3Type):
			self.switch_to_amf3()
			self.write_value(value)
		else:
			assert type(value) == StrictArray, 'AMF0 type is not supported except strict-array'

		t = type(value)
		funs = {
				StrictArray: ('0x0a', self.write_strict_array),
				}

		b, func = funs[t]
		self.fp.write(b)
		func(value)

	def write_value3(self, value):
		t = type(value)
		funs = {
				NULL  : ('0x01', self.write_null),
				FALSE : ('0x02', self.write_false),
				TRUE  : ('0x03', self.write_true),
				int   : ('0x04', self.write_u29),
				float : ('0x05', self.write_double),
				str   : ('0x06', self.write_utf8_vr),
				Array : ('0x09', self.write_array),
				Object: ('0x0a', self.write_object),
				}
		b, func = funs[t]
		self.fp.write(b)
		func(value)

	def switch_to_amf0(self):
		self.write_value = self.write_value0

	def switch_to_amf3(self):
		self.fp.write('0x11')
		self.write_value = self.write_value3


	write_value = write_value0

if __name__ == '__main__':
	pass





# vim: foldmethod=marker:
