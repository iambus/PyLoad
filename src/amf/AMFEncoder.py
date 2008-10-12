
from struct import *
from AMFTypes import *


class AMFEncoder:
	def __init__(self, packet, fp):
		self.packet = packet
		if fp != None:
			self.fp = fp
		else:
			import cStringIO
			self.fp = cStringIO.StringIO()

		self.string_reference_table = []
		self.trait_reference_table = []
		self.complex_object_reference_table = []

		self.string_rref_table = {}
		self.trait_rref_table = {}
		self.complex_rref_table = {}

	########################################
	# {{{ encode: encode AMFPacket into stream
	def encode(self):
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
			self.write_value(message.value)
			self.switch_to_amf0()

		if hasattr(self.fp, 'getvalue'):
			return self.fp.getvalue()
	# }}}
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
		assert self.write_value == self.write_value0, 'write_utf8 should be only use in AMF0'
		utf8 = s.encode('utf-8')
		self.write_u16(len(utf8))
		self.fp.write(utf8)

	def write_utf8_long(self, s):
		utf8 = s.encode('utf-8')
		self.write_u32(len(utf8))
		self.fp.write(utf8)

	def write_utf8_vr(self, s):
		if s == '':
			self.fp.write('\x01')
			return
		utf8 = s.encode('utf-8')
		index = self.string_rref_table.get(utf8)
		if index != None:
			u = index << 1
			self.write_u29(u)
		else:
			u = (len(utf8) << 1) | 1
			self.write_u29(u)
			self.fp.write(utf8)

			index = len(self.string_reference_table)
			self.string_reference_table.append(utf8)
			self.string_rref_table[utf8] = index

	def write_null(self, ignore):
		# Nothing to write
		pass

	def write_false(self, ignore):
		# Nothing to write
		pass

	def write_true(self, ignore):
		# Nothing to write
		pass

	def write_double(self, d):
		self.fp.write(pack('!d', d))

	# }}}
	########################################
	# {{{ write arrays and objects

	def write_strict_array(self, array):
		array = array.array
		self.write_u32(len(array))
		for i in array:
			self.write_value(i)

	def write_array(self, arrayref):
		index = self.put_array(arrayref)
		if index != None:
			# array-ref
			u = index << 1
			self.write_u29(u)
		else:
			array = arrayref.array
			assoc_values = array.assoc
			list_values = array.list

			dense_portion = len(list_values)
			u = (dense_portion << 1) | 1
			self.write_u29(u)

			for k, v in assoc_values:
				self.write_utf8_vr(k)
				self.write_value(v)
			self.write_utf8_vr('')
			for item in list_values:
				self.write_value(item)

	def write_object(self, objref):
		index = self.put_object(objref)
		obj = objref.object
		if index != None:
			# object-ref
			u = index << 1
			self.write_u29(u)
		else:
			traitref = obj.trait
			trait = traitref.trait
			index = self.put_trait(traitref)
			if index != None:
				# trait-ref
				u = (index << 2) | 1
				self.write_u29(u)
				for member in obj.members:
					self.write_value(member)
				if trait.is_dynamic():
					for k, v in obj.dynamic_members:
						self.write_utf8_vr(k)
						self.write_value(v)
					self.write_utf8_vr('')
			else:
				if isinstance(trait, TraitExt):
					assert isinstance(obj, ExtObject)
					#XXX: are the high 26 bits always 0?
					u = (0 << 3) | 7
					self.write_u29(u)
					self.write_utf8_vr(trait.classname)
					self.write_value(obj.members[0])
				elif isinstance(trait, StaticTrait):
					assert isinstance(obj, StaticObject)
					u = (len(trait.member_names) << 4) | 3
					self.write_u29(u)
					self.write_utf8_vr(trait.classname)
					for name in trait.member_names:
						self.write_utf8_vr(name)
					for value in obj.members:
						self.write_value(value)
				elif isinstance(trait, DynamicTrait):
					assert isinstance(obj, DynamicObject)
					u = (len(trait.member_names) << 4) | 11
					assert u == 11, 'Often the static members of dynamic object is empty'
					self.write_u29(u)
					self.write_utf8_vr(trait.classname)
					for name in trait.member_names:
						self.write_utf8_vr(name)
					for value in obj.members:
						self.write_value(value)
					for k, v in obj.dynamic_members:
						self.write_utf8_vr(k)
						self.write_value(v)
					self.write_utf8_vr('')
				else:
					raise TypeError('Unknown object type: %s, trait: %s' % (obj.__class__, trait.__class__))

	def put_trait(self, traitref):
		'return index if the trait already registered (which means the index should be used as reference)'
		assert isinstance(traitref, TraitRef)
		if self.trait_rref_table.has_key(traitref.refindex):
			return self.trait_rref_table[traitref.refindex]
		else:
			index = len(self.trait_reference_table)
			self.trait_reference_table.append(index)
			self.trait_rref_table[traitref.refindex] = index

	def put_object(self, objref):
		'return index if the object already registered (which means the index should be used as reference)'
		assert isinstance(objref, ObjectRef)
		return self.put_complext_object(objref)

	def put_array(self, arrayref):
		'return index if the object already registered (which means the index should be used as reference)'
		assert isinstance(arrayref, ArrayRef)
		return self.put_complext_object(arrayref)

	def put_complext_object(self, ref):
		if self.complex_rref_table.has_key(ref.refindex):
			return self.complex_rref_table[ref.refindex]
		else:
			index = len(self.complex_object_reference_table)
			self.complex_object_reference_table.append(index)
			self.complex_rref_table[ref.refindex] = index

	# }}}
	########################################
	# {{{ write values
	def write_value0(self, value):
		if isinstance(value, AMF3Type):
			self.switch_to_amf3()
			self.write_value(value)
			return
		else:
			assert value.__class__ in [StrictArray, str, unicode], 'AMF0 type is not supported except strict-array and str. %s is not supported' % value.__class__

		t = value.__class__
		funs = {
				str        : ('\x02', self.write_utf8),
				unicode    : ('\x02', self.write_utf8),
				StrictArray: ('\x0a', self.write_strict_array),
				}
		assert funs.has_key(t), '%s is not supported in AMF0' % t

		b, func = funs[t]
		self.fp.write(b)
		func(value)

	def write_value3(self, value):
		t = value.__class__
		funs = {
				NULL     : ('\x01', self.write_null),
				FALSE    : ('\x02', self.write_false),
				TRUE     : ('\x03', self.write_true),
				int      : ('\x04', self.write_u29),
				float    : ('\x05', self.write_double),
				str      : ('\x06', self.write_utf8_vr),
				unicode  : ('\x06', self.write_utf8_vr),
				ArrayRef : ('\x09', self.write_array),
				ObjectRef: ('\x0a', self.write_object),
				}
		assert funs.has_key(t), '%s is not supported in AMF3' % t
		b, func = funs[t]
		self.fp.write(b)
		func(value)

	def switch_to_amf0(self):
		self.write_value = self.write_value0

	def switch_to_amf3(self):
		self.fp.write('\x11')
		self.write_value = self.write_value3

	write_value = write_value0
	# }}}
	########################################

if __name__ == '__main__':
	from AMFDecoder import AMFDecoder
	from cStringIO import StringIO
	fp = open('login.txt', 'rb')
	fp = open('login-response.txt', 'rb')
	fp = open('client-ping.txt', 'rb')
	fp = open('client-ping-response.txt', 'rb')
	decoder = AMFDecoder(fp)
	packet = decoder.decode()
	#print packet
	fp = StringIO()
	encoder = AMFEncoder(packet, fp)
	encoder.encode()
	v = fp.getvalue()
	fp = open('x', 'wb')
	fp.write(v)
	fp.close()


# vim: foldmethod=marker:
