
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

class Date(AMF3Type):
	def __init__(self, double):
		AMF3Type.__init__(self)
		self.double = double
	def __str__(self):
		return self.double
	def __repr__(self):
		return repr(self.double)

class DateRef(AMF3Type):
	def __init__(self, date, index):
		AMF3Type.__init__(self)
		assert isinstance(date, Date)
		assert type(index) == int
		self.date = date
		self.refindex = index
	def __str__(self):
		return str(self.date)
	def __repr__(self):
		return str(self)
	def get_id(self):
		return refindex

class Trait(AMF3Type):
	def __init__(self, classname):
		AMF3Type.__init__(self)
		assert classname != None
		self.classname = classname
		self.member_names = []
	def get_class_name(self):
		return self.classname
	def get_member_names(self):
		return self.member_names
	def instance(self, ref):
		raise NotImplementedError('Trait is abstract')

class StaticTrait(Trait):
	def __init__(self, classname):
		Trait.__init__(self, classname)
	def is_dynamic(self):
		return False
	def instance(self, ref):
		return StaticObject(ref)
	def __str__(self):
		return "trait<%s>" % self.classname
	def __repr__(self):
		return str(self)

class DynamicTrait(Trait):
	def __init__(self, classname):
		Trait.__init__(self, classname)
	def is_dynamic(self):
		return True
	def instance(self, ref):
		return DynamicObject(ref)
	def __str__(self):
		return "dynamic-trait<%s>" % self.classname
	def __repr__(self):
		return str(self)

class TraitExt(Trait):
	def __init__(self, classname):
		Trait.__init__(self, classname)
		self.member_names.append(u'value')
	def is_dynamic(self):
		return False
	def instance(self, ref):
		return ExtObject(ref)
	def __str__(self):
		return "trait-ext<%s>" % self.classname
	def __repr__(self):
		return str(self)

class TraitRef(AMF3Type):
	def __init__(self, trait, index):
		AMF3Type.__init__(self)
		assert isinstance(trait, Trait)
		assert type(index) == int
		self.trait = trait
		self.refindex = index
	def get_referenced(self):
		return self.trait
	def get_class_name(self):
		return self.get_referenced().get_class_name()
	def get_member_names(self):
		return self.get_referenced().get_member_names()
	def get_id(self):
		return refindex
	def instance(self):
		return self.get_referenced().instance(self)
	def is_dynamic(self):
		return self.get_referenced().is_dynamic()
	def __str__(self):
		return 'trait-ref:%s:%s' % (self.refindex, self.get_class_name())
	def __repr__(self):
		return str(self)

class Object(AMF3Type):
	def __init__(self, trait):
		AMF3Type.__init__(self)
		assert isinstance(trait, TraitRef), 'Object must has a TraitRef instead of Trait'
		self.trait = trait
		self.members = []

class StaticObject(Object):
	def __init__(self, trait):
		Object.__init__(self, trait)
	def __str__(self):
		trait = self.trait.get_referenced()
		assert trait.__class__ == StaticTrait, 'StaticObject should have StaticTrait, but got %s' % trait.__class__
		x = []
		member_names = trait.get_member_names()
		for i in range(len(member_names)):
			name = member_names[i]
			value = self.members[i]
			x.append('%s: %s' % (repr(name), repr(value)))
		return "static-object<{%s}>={%s}" % (trait, ', '.join(x))
	def __repr__(self):
		return str(self)

class DynamicObject(Object):
	def __init__(self, trait):
		Object.__init__(self, trait)
		self.dynamic_members = []
	def __str__(self):
		trait = self.trait.get_referenced()
		assert trait.__class__ == DynamicTrait
		assert len(self.members) == 0
		return "dynamic-object<{%s}>=%s" % (trait, self.dynamic_members)
	def __repr__(self):
		return str(self)

class ExtObject(Object):
	def __init__(self, trait):
		Object.__init__(self, trait)
	def get_value(self):
		return self.members[0]
	def set_value(self, value):
		assert len(self.members) == 0, 'Often the value of ext-object should be set only once. If you set it twice, we have to clear the members first in the code of set_value.'
		self.members.append(value)
	def __str__(self):
		trait = self.trait.get_referenced()
		assert trait.__class__ == TraitExt
		return "ext-object<{%s}>=(%s)" % (trait, self.members[0])
	def __repr__(self):
		return str(self)

class ObjectRef(AMF3Type):
	def __init__(self, object, index):
		AMF3Type.__init__(self)
		assert isinstance(object, Object)
		assert type(index) == int
		self.object = object
		self.refindex = index
	def __str__(self):
		return str(self.object)
	def __repr__(self):
		return str(self)
	def get_id(self):
		return refindex


class Array(AMF3Type):
	def __init__(self):
		AMF3Type.__init__(self)
		self.list = []
		self.assoc = []
	def __str__(self):
		assert len(self.list) == 0 or len(self.assoc) == 0
		if not self.assoc:
			return "list-array=%s" % self.list
		else:
			return "assoc-array=%s" % self.assoc
	def __repr__(self):
		return str(self)

class ArrayRef(AMF3Type):
	def __init__(self, array, index):
		AMF3Type.__init__(self)
		assert isinstance(array, Array)
		assert type(index) == int
		self.array = array
		self.refindex = index
	def __str__(self):
		return str(self.array)
	def __repr__(self):
		return str(self)
	def get_id(self):
		return refindex

class ByteArray(AMF3Type):
	def __init__(self, content):
		AMF3Type.__init__(self)
		assert isinstance(content, str)
		self.content = content
	def __str__(self):
		return 'ByteArray={%s}' % repr(self.content)
	def __repr__(self):
		return str(self)

class ByteArrayRef(AMF3Type):
	def __init__(self, array, index):
		AMF3Type.__init__(self)
		assert isinstance(array, ByteArray)
		assert type(index) == int
		self.array = array
		self.refindex = index
	def __str__(self):
		return str(self.array)
	def __repr__(self):
		return str(self)
	def get_id(self):
		return refindex

class XML(AMF3Type):
	def __init__(self, content):
		AMF3Type.__init__(self)
		assert isinstance(content, str) or isinstance(content, unicode)
		self.content = content
	def __str__(self):
		return 'XML={%s}' % repr(self.content)
	def __repr__(self):
		return str(self)

class XMLRef(AMF3Type):
	def __init__(self, xml, index):
		AMF3Type.__init__(self)
		assert isinstance(xml, XML)
		assert type(index) == int
		self.xml = xml
		self.refindex = index
	def __str__(self):
		return str(self.xml)
	def __repr__(self):
		return str(self)
	def get_id(self):
		return refindex

# AMF0
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



