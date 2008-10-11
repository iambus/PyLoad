
class AMF0Type:
	def __init__(self):
		self.version = 0

class AMF3Type:
	def __init__(self):
		self.version = 3

class NULL:
	def __str__(self):
		return 'null'
	def __repr__(self):
		return str(self)

class TRUE:
	def __str__(self):
		return 'True'
	def __repr__(self):
		return str(self)

class FALSE:
	def __str__(self):
		return 'False'
	def __repr__(self):
		return str(self)

class String:
	def __init__(self, string):
		self.string = string
	def __str__(self):
		return self.string
	def __repr__(self):
		return repr(self.string)

#XXX: should we use StringRef?
class StringRef(AMF3Type):
	def __init__(self, table, index):
		AMF3Type.__init__(self)
		raise RuntimeError("I'm trying to refactor code to remove this type, please don't use it now")
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

class Trait(AMF3Type):
	def __init__(self, is_dynamic = False):
		AMF3Type.__init__(self)
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

class TraitExt(AMF3Type):
	def __init__(self):
		AMF3Type.__init__(self)
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

class TraitRef(AMF3Type):
	def __init__(self, trait, index):
		AMF3Type.__init__(self)
		self.trait = trait
		self.refindex = index
	def get_referenced(self):
		return self.trait
	def get_class_name(self):
		return self.get_referenced().get_class_name()
	def get_member_names(self):
		return self.get_referenced().get_member_names()
	def is_dynamic(self):
		return self.get_referenced().is_dynamic()
	def __str__(self):
		return 'trait-ref:%s:%s' % (self.refindex, self.get_class_name())
	def __repr__(self):
		return str(self)

#XXX: should we always use ObjectRef?
class Object(AMF3Type):
	def __init__(self, trait):
		AMF3Type.__init__(self)
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

class ObjectRef(AMF3Type):
	def __init__(self, object, index):
		AMF3Type.__init__(self)
		self.object = object
		self.refindex = index
	def __str__(self):
		return str(self.object)
	def __repr__(self):
		return str(self)


class Array(AMF3Type):
	def __init__(self):
		AMF3Type.__init__(self)
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

class ComplexObjectRef(AMF3Type):
	def __init__(self, table, index):
		AMF3Type.__init__(self)
		raise RuntimeError("I'm trying to refactor code to remove this type, please don't use it now")
		self.reftable = table
		self.refindex = index
	def get_referenced(self):
		return self.reftable[self.refindex]
	def __str__(self):
		return 'complex-ref-%s' % self.get_referenced()
	def __repr__(self):
		return str(self)

class StrictArray(AMF0Type):
	def __init__(self, array):
		AMF0Type.__init__(self)
		self.array = array
	def __str__(self):
		return 'strict-array=%s' % self.array
	def __repr__(self):
		return str(self)

##################################################

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

		self.trait_reference_table = None
		self.string_reference_table = None
		self.complex_object_reference_table = None

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


##################################################



