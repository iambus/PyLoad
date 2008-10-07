
from struct import *

##################################################

# {{{ AMF Types
class NULL:
	def __str__(self):
		return 'null'
	def __repr__(self):
		return str(self)

class StringRef:
	def __init__(self, table, index):
		self.refindex = index
		self.reftable = table
	def get_referenced(self):
		return self.reftable[self.refindex]
	def get(self):
		return self.get_referenced()
	def __str__(self):
		return 'string-ref:%s:%s' % (self.refindex, self.get_referenced())
	def __repr__(self):
		return str(self)

class Trait:
	def __init__(self, is_dynamic = False):
		self.classname = None
		self.member_names = []
		self.dynamic = is_dynamic
	def get_class_name(self):
		return self.classname
	def get_member_names(self):
		return self.member_names
	def is_dynamic(self):
		return self.dynamic
	def __str__(self):
		return "trait<%s>" % self.classname
	def __repr__(self):
		return str(self)

class TraitRef:
	def __init__(self, table, index):
		self.refindex = index
		self.reftable = table
	def get_referenced(self):
		return self.reftable[self.refindex]
	def get_class_name(self):
		return self.get_referenced().get_class_name()
	def get_member_names(self):
		return self.reftable[self.refindex].get_member_names()
	def is_dynamic(self):
		return self.get_referenced().is_dynamic()
	def __str__(self):
		return 'trait-ref:%s:%s' % (self.refindex, self.get_class_name())
	def __repr__(self):
		return str(self)

class TraitExt:
	def __init__(self):
		self.classname = None
		self.member_names = [u'value']
	def get_class_name(self):
		return self.classname
	def get_member_names(self):
		return self.member_names
	def is_dynamic(self):
		return False
	def __str__(self):
		return "trait-ext<%s>" % self.classname
	def __repr__(self):
		return str(self)

class Object:
	def __init__(self, trait):
		self.trait = trait
		self.members = []
		self.dynamic_members = {}
	def __str__(self):
		if not self.trait.is_dynamic():
			x = []
			member_names = self.trait.get_member_names()
			for i in range(len(member_names)):
				name = member_names[i]
				value = self.members[i]
				x.append('%s: %s' % (repr(name), repr(value)))
			return "object<{%s}>={%s}" % (self.trait, ', '.join(x))
		else:
			assert len(self.members) == 0
			return "dynamic-object<{%s}>=%s" % (self.trait, self.dynamic_members)
	def __repr__(self):
		return str(self)

class Array:
	def __init__(self):
		self.list = []
		self.assoc = {}
	def __str__(self):
		assert len(self.list) == 0 or len(self.assoc) == 0
		if not self.assoc:
			return "list-array=%s" % self.list
		else:
			return "assoc-array=%s" % self.assoc
	def __repr__(self):
		return str(self)

class ComplexObjectRef:
	def __init__(self, table, index):
		#raise RuntimeError('Note: This piece of code is not tested yet.')
		self.reftable = table
		self.refindex = index
	def get_referenced(self):
		return self.reftable[self.refindex]
	def __str__(self):
		return 'complex-ref-%s' % self.get_referenced()
	def __repr__(self):
		return str(self)

class StrictArray:
	def __init__(self, array):
		self.array = array
	def __str__(self):
		return 'strict-array=%s' % self.array
	def __repr__(self):
		return str(self)

class HeaderType:
	def __init__(self):
		self.header_name = None
		self.must_understand = None
		self.header_length = None
		self.value = None
	def __str__(self):
		return "header-name: %s\nmust-understand: %s\nvalue: %s\n" % (self.header_name, self.must_understand, self.value)
	def __repr__(self):
		return str(self)

class MessageType:
	def __init__(self):
		self.target_uri = None
		self.response_uri = None
		self.message_length = None
		self.value = None
	def __str__(self):
		return "target-uri: %s\nresponse-uri: %s\nvalue: %s\n" % (self.target_uri, self.response_uri, self.value)
	def __repr__(self):
		return str(self)

class AMFPacket:
	def __init__(self):
		self.version = None
		self.header_count = None
		self.headers = []
		self.message_count = None
		self.messages = []

	def __str__(self):
		h = ''
		for header in self.headers:
			h += str(header) + '\n'
		m = ''
		for message in self.messages:
			m += str(message) + '\n'
		return "[Version]\n%s\n\n[Headers]\n%s\n\n[Messages]\n%s\n\n" % (self.version, h, m)
	def __repr__(self):
		return str(self)
# }}}

##################################################

class AMFDecoder:
	def __init__(self, fp):
		self.fp = fp
		self.trait_reference_table = []
		self.string_reference_table = []
		self.complex_object_reference_table = []

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
			packet.messages.append(message)
			self.switch_to_amf0()

		assert self.fp.read() == '', 'Decode error: something left in stream...'

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
		return (bx << 8) | b4

	def read_utf8_n(self, n):
		return self.fp.read(n).decode('utf-8')

	def read_utf8(self):
		bytes_length = self.read_u16()
		return self.read_utf8_n(bytes_length)

	def read_utf8_long(self):
		bytes_length = self.read_u32()
		return self.read_utf8_n(bytes_length)

	def read_utf8_vr(self):
		u = self.read_u29()
		if u & 1 == 0:
			# U29S-ref
			index = u >> 1
			return StringRef(self.string_reference_table, index)
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
		return False

	def read_true(self):
		return True

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

	#AMF0
	def read_typed_object(self):
		raise NotImplementedError()
		class_name = self.read_utf8()
		print class_name

	def read_array(self):
		u = self.read_u29()

		if u & 1 == 0:
			index = u >> 1
			# XXXXXXXXXXXXXXXXXXXXXXXXXXXX 0
			# U29O-ref
			return ComplexObjectRef(self.complex_object_reference_table, index)
		else:
			dense_portion = u >> 1

			array = Array()

			name = self.read_utf8_vr()
			assert name == '', 'Please review the code and make sure the associative array is supported correctly'
			while name != '':
				value = self.read_value()
				array.assoc[name] = value
				print 'assoc-value: [', name, '=>', value, ']'
				name = self.read_utf8_vr()

			for i in range(dense_portion):
				array.list.append(self.read_value())

			assert len(array.assoc) == 0 or len(array.list) == 0
			return array

	def read_object(self):
		u = self.read_u29()
		if u & 1 == 0:
			index = u >> 1
			# XXXXXXXXXXXXXXXXXXXXXXXXXXXX 0
			# U29O-ref
			return ComplexObjectRef(self.complex_object_reference_table, index)
		elif u & 2 == 0:
			index  = u >> 2
			# XXXXXXXXXXXXXXXXXXXXXXXXXXX 01
			# U29O-traits-ref
			trait = TraitRef(self.trait_reference_table, index)
			obj = Object(trait)
			self.complex_object_reference_table.append(obj)
			member_names = trait.get_member_names()
			for name in member_names:
				obj.members.append(self.read_value())
			if trait.get_referenced().is_dynamic():
				name = self.read_utf8_vr()
				while name != '':
					value = self.read_value()
					obj.dynamic_members[name] = value
					name = self.read_utf8_vr()
			return obj
		elif u & 4:
			# XXXXXXXXXXXXXXXXXXXXXXXXXXX 111
			assert (u >> 3) == 0
			# U29O-traits-ext
			trait = TraitExt()
			trait.classname = self.read_utf8_vr()
			self.trait_reference_table.append(trait)

			obj = Object(trait)
			self.complex_object_reference_table.append(obj)
			obj.members.append(self.read_value())
			return obj
		else:
			# XXXXXXXXXXXXXXXXXXXXXXXXXX? 011
			# U29O-traits
			if u & 8:
				# XXXXXXXXXXXXXXXXXXXXXXXXXX 1011
				# dynamic
				trait = Trait(is_dynamic = True)
				trait.classname = self.read_utf8_vr()
				#XXX: can dynamic trait has class name?
				assert trait.classname == ''
				#XXX: dynamic trait shold be put into reference table?
				self.trait_reference_table.append(trait)

				member_count = u >> 4
				#XXX: can dynamic trait has static memebers?
				assert member_count == 0

				obj = Object(trait)
				self.complex_object_reference_table.append(obj)

				name = self.read_utf8_vr()
				while name != '':
					#XXX: should the dynamic fields be put in trait?
					#trait.member_names.append(name)
					value = self.read_value()
					obj.dynamic_members[name] = value
					name = self.read_utf8_vr()

				return obj
			else:
				# XXXXXXXXXXXXXXXXXXXXXXXXXX 0011
				# not dynamic
				trait = Trait()
				trait.classname = self.read_utf8_vr()
				self.trait_reference_table.append(trait)

				member_count = u >> 4
				for i in range(member_count):
					trait.member_names.append(self.read_utf8_vr())

				obj = Object(trait)
				self.complex_object_reference_table.append(obj)
				for i in range(member_count):
					member_value = self.read_value()
					obj.members.append(member_value)

				return obj
	# }}}

	########################################

	# {{{ read values
	def read_value0(self):
		x = self.read_byte()
		if x == 0x11:
			self.switch_to_amf3()
			return self.read_value3()
		funs = {
				0x02: self.read_utf8,
				0x0a: self.read_strict_array,
				0x10: self.read_typed_object,
			   }
		return funs[x]()

	def read_value3(self):
		x = self.read_byte()
		funs = {
				0x01: self.read_null,
				0x02: self.read_false,
				0x03: self.read_true,
				0x04: self.read_u29,
				0x05: self.read_double,
				0x06: self.read_utf8_vr,
				0x09: self.read_array,
				0x0a: self.read_object,
			   }
		return funs[x]()

	def switch_to_amf0(self):
		self.read_value = self.read_value0

	def switch_to_amf3(self):
		self.read_value = self.read_value3

	read_value = read_value0
	# }}}

	########################################


if __name__ == '__main__':
	fp = open('client-ping.txt', 'rb')
	fp = open('login-response.txt', 'rb')
	decoder = AMFDecoder(fp)
	packet = decoder.decode()
	print packet

# vim: foldmethod=marker:
