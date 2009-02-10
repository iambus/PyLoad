
from struct import *
from AMFTypes import *
from AMFExtAlias import *

##################################################
def decode(source):
	return AMFDecoder(source).decode()

##################################################

class AMFDecoder:
	def __init__(self, fp):
		if type(fp) == str or type(fp) == unicode:
			from cStringIO import StringIO
			self.fp = StringIO(fp)
		else:
			self.fp = fp
		self.trait_reference_table = []
		self.string_reference_table = []
		self.complex_object_reference_table = []

		self.read_value0_mappings = {
				0x02: self.read_utf8,
				0x0a: self.read_strict_array,
				#0x10: self.read_typed_object,
			   }
		self.read_value3_mappings = {
				0x01: self.read_null,
				0x02: self.read_false,
				0x03: self.read_true,
				0x04: self.read_u29,
				0x05: self.read_double,
				0x06: self.read_utf8_vr,
				#0x07: self.read_xml_doc,
				0x08: self.read_date,
				0x09: self.read_array,
				0x0a: self.read_object,
				0x0b: self.read_xml,
				0x0c: self.read_byte_array,
			   }

	########################################
	# {{{ decode: return a AMFPacket object
	def decode(self):
		packet = AMFPacket()
		packet.version = self.read_u16()
		assert packet.version == 3, 'Only AMF 3 is supported'

		packet.header_count = self.read_u16()

		for i in range(packet.header_count):
			header = HeaderType()
			header.header_name = self.read_utf8()
			header.must_understand = self.read_byte() != 0
			header.header_length = self.read_u32()
			header.value = self.read_value()

			self.trait_reference_table = []
			self.string_reference_table = []
			self.complex_object_reference_table = []

			packet.headers.append(header)
			self.switch_to_amf0()


		packet.message_count = self.read_u16()

		for i in range(packet.message_count):
			message = MessageType()
			message.target_uri = self.read_utf8()
			message.response_uri = self.read_utf8()
			message.message_length = self.read_u32()
			#TODO: use messsage-length for assert
			message.value = self.read_value()

			self.trait_reference_table = []
			self.string_reference_table = []
			self.complex_object_reference_table = []

			packet.messages.append(message)
			self.switch_to_amf0()

		rest = self.fp.read()
		if rest != '':
			if rest != '\r\n':
				raise RuntimeError('Decode error: something left in stream...\nlength: %d\n%s' % (len(rest), repr(rest)))

		return packet
	# }}}

	########################################

	# {{{ read basic types
	def read_byte(self):
		return ord(self.fp.read(1))

	def read_u16(self):
		return unpack('>h', self.fp.read(2))[0]

	def read_u32(self):
		return unpack('>i', self.fp.read(4))[0]

	def read_u29(self):
		b1 = self.read_byte()
		bx = b1 & 0x7f
		if (b1 & 0x80) == 0:
			return bx
		b2 = self.read_byte()
		bx = (bx << 7) | (b2 & 0x7f)
		if (b2 & 0x80) == 0:
			return bx
		b3 = self.read_byte()
		bx = (bx << 7) | (b3 & 0x7f)
		if (b3 & 0x80) == 0:
			return bx
		b4 = self.read_byte()
		bx = (bx << 8) | b4
		if (bx & 0x10000000):
			#XXX: negative number?
			return bx - 0x20000000
		else:
			return bx

	def read_utf8_n(self, n):
		return self.fp.read(n).decode('utf-8')

	def read_utf8(self):
		assert self.read_value == self.read_value0, 'read_utf8 should be only use in AMF0'
		bytes_length = self.read_u16()
		return self.read_utf8_n(bytes_length)

	def read_utf8_long(self):
		assert self.read_value == self.read_value0, 'read_utf8_long should be only use in AMF0'
		assert False, 'Dev note: utf8-long is used, should we differ utf8 and utf-long using different String types?'
		bytes_length = self.read_u32()
		return self.read_utf8_n(bytes_length)

	def read_utf8_vr(self):
		u = self.read_u29()
		if u & 1 == 0:
			# U29S-ref
			index = u >> 1
			#return String(self.string_reference_table[index])
			return self.string_reference_table[index]
			#raise NotImplementedError()
		else:
			# U29S-value *(UTF-8-char)
			bytes_length = u >> 1
			string = self.read_utf8_n(bytes_length)
			if string:
				self.string_reference_table.append(string)
			return string

	def read_null(self):
		return NULL()

	def read_false(self):
		return FALSE()

	def read_true(self):
		return TRUE()

	def read_double(self):
		return unpack('!d', self.fp.read(8))[0]
	# }}}

	########################################
	# {{{ read arrays and objects

	#AMF0
	def read_strict_array(self):
		array_count = self.read_u32()
		array = []
		for i in range(array_count):
			array.append(self.read_value())
		return StrictArray(array)


	#AMF3

	def read_date(self):
		u = self.read_u29()

		if u & 1 == 0:
			index = u >> 1
			# XXXXXXXXXXXXXXXXXXXXXXXXXXXX 0
			# U29O-ref
			return DateRef(self.complex_object_reference_table[index], index)
		else:
			# 0000000000000000000000000000 1
			# U29D-value
			assert u == 1, 'The high 28 bits should not be used'
			date = Date(self.read_double())
			return self.put_date(date)

	def read_array(self):
		u = self.read_u29()

		if u & 1 == 0:
			index = u >> 1
			# XXXXXXXXXXXXXXXXXXXXXXXXXXXX 0
			# U29O-ref
			return ArrayRef(self.complex_object_reference_table[index], index)
		else:
			dense_portion = u >> 1

			array = Array()
			aref = self.put_array(array)

			name = self.read_utf8_vr()
			while name != '':
				value = self.read_value()
				array.assoc.append((name, value))
				name = self.read_utf8_vr()

			for i in range(dense_portion):
				array.list.append(self.read_value())

			assert len(array.assoc) == 0 or len(array.list) == 0
			return aref

	# {{{ read_object
	def read_object(self):
		u = self.read_u29()
		if u & 1 == 0:
			index = u >> 1
			# XXXXXXXXXXXXXXXXXXXXXXXXXXXX 0
			# U29O-ref
			return ObjectRef(self.complex_object_reference_table[index], index)
		elif u & 2 == 0:
			index  = u >> 2
			# XXXXXXXXXXXXXXXXXXXXXXXXXXX 01
			# U29O-traits-ref
			trait = TraitRef(self.trait_reference_table[index], index)
			assert not isinstance(trait.trait, TraitRef)
			obj = trait.instance()
			objref = self.put_object(obj)
			if trait.is_external():
				obj.decode(self)
				#obj.value = self.read_value()
			else:
				member_names = trait.get_member_names()
				for name in member_names:
					obj.members.append(self.read_value())
				if trait.is_dynamic():
					name = self.read_utf8_vr()
					while name != '':
						value = self.read_value()
						obj.dynamic_members.append((name, value))
						name = self.read_utf8_vr()
			return objref
		elif u & 4:
			# XXXXXXXXXXXXXXXXXXXXXXXXXXX 111
			assert (u >> 3) == 0
			# U29O-traits-ext
			alias_name = self.read_utf8_vr()
			trait = TraitExt(alias_name)
			trait = self.put_trait(trait)

			ext_type = find_alias(alias_name)
			obj = ext_type(trait)
			index = len(self.complex_object_reference_table)
			self.complex_object_reference_table.append(obj)
			obj.decode(self)

			return ObjectRef(obj, index)
		else:
			# XXXXXXXXXXXXXXXXXXXXXXXXXX? 011
			# U29O-traits
			if u & 8:
				# XXXXXXXXXXXXXXXXXXXXXXXXXX 1011
				# dynamic
				trait = DynamicTrait(self.read_utf8_vr())
				#XXX: can dynamic trait has class name?
				assert trait.classname == ''
				#XXX: dynamic trait shold be put into reference table?
				trait = self.put_trait(trait)

				member_count = u >> 4
				#XXX: can dynamic trait has static memebers?
				assert member_count == 0

				obj = DynamicObject(trait)
				objref = self.put_object(obj)

				#TODO: read static members if this is possiable
				for i in range(member_count):
					member_value = self.read_value()
					obj.members.append(member_value)

				name = self.read_utf8_vr()
				while name != '':
					#XXX: should the dynamic fields be put in trait?
					#trait.member_names.append(name)
					value = self.read_value()
					obj.dynamic_members.append((name, value))
					name = self.read_utf8_vr()

				return objref
			else:
				# XXXXXXXXXXXXXXXXXXXXXXXXXX 0011
				# not dynamic
				trait = StaticTrait(self.read_utf8_vr())
				trait = self.put_trait(trait)

				member_count = u >> 4
				for i in range(member_count):
					trait.get_member_names().append(self.read_utf8_vr())

				obj = StaticObject(trait)
				objref = self.put_object(obj)
				for i in range(member_count):
					member_value = self.read_value()
					obj.members.append(member_value)

				return objref
	# }}}

	def read_xml(self):
		u = self.read_u29()

		if u & 1 == 0:
			index = u >> 1
			# XXXXXXXXXXXXXXXXXXXXXXXXXXXX 0
			# U29O-ref
			return XMLRef(self.complex_object_reference_table[index], index)
		else:
			xml_length = u >> 1
			xml_content = self.read_utf8_n(xml_length)
			return self.put_complex_object(XML(xml_content), XMLRef)

	def read_byte_array(self):
		u = self.read_u29()

		if u & 1 == 0:
			index = u >> 1
			# XXXXXXXXXXXXXXXXXXXXXXXXXXXX 0
			# U29O-ref
			return ByteArrayRef(self.complex_object_reference_table[index], index)
		else:
			array_length = u >> 1
			array_content = self.fp.read(array_length)
			array = ByteArray(array_content)
			return self.put_complex_object(array, ByteArrayRef)

	def put_trait(self, trait):
		index = len(self.trait_reference_table)
		self.trait_reference_table.append(trait)
		return TraitRef(trait, index)

	def put_object(self, obj):
		index = len(self.complex_object_reference_table)
		self.complex_object_reference_table.append(obj)
		return ObjectRef(obj, index)

	def put_array(self, array):
		index = len(self.complex_object_reference_table)
		self.complex_object_reference_table.append(array)
		return ArrayRef(array, index)

	def put_date(self, date):
		index = len(self.complex_object_reference_table)
		self.complex_object_reference_table.append(date)
		return DateRef(date, index)

	def put_complex_object(self, obj, refclass):
		assert isinstance(obj, AMF3Type)
		index = len(self.complex_object_reference_table)
		self.complex_object_reference_table.append(obj)
		return refclass(obj, index)

	# }}}
	########################################

	# {{{ read values
	def read_value0(self):
		x = self.read_byte()
		if x == 0x11:
			self.switch_to_amf3()
			return self.read_value3()
		funs = self.read_value0_mappings
		return funs[x]()

	def read_value3(self):
		x = self.read_byte()
		funs = self.read_value3_mappings
		return funs[x]()

	def switch_to_amf0(self):
		self.read_value = self.read_value0

	def switch_to_amf3(self):
		self.read_value = self.read_value3

	read_value = read_value0
	# }}}

	########################################


if __name__ == '__main__':
	sample_path = 'samples/login.txt'
	sample_path = 'samples/login-response.txt'
	sample_path = 'samples/client-ping.txt'
	sample_path = 'samples/client-ping-response.txt'
	sample_path = 'samples/5.txt'
	sample_path = 'samples/6.txt'
	sample_path = 'samples/7.txt'
	sample_path = 'samples/9.txt'
	sample_path = 'samples/13.txt'
	sample_path = 'samples/12.txt'
	sample_path = 'samples/blazeds-3.txt'

	fp = open(sample_path, 'rb')
	decoder = AMFDecoder(fp)
	packet = decoder.decode()
	print packet

# vim: foldmethod=marker:
