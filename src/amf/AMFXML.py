
from xml.dom import minidom
from AMFTypes import *

##################################################
# {{{ class ToXML
class ToXML:
	def __init__(self, packet):
		self.packet = packet

		self.complex_object_set = set()
		self.trait_set = set()

		self.to_xml()

	##################################################

	def to_xml(self):
		self.doc = minidom.Document()
		doc = self.doc

		packet = self.packet

		root = doc.createElement('packet')
		doc.appendChild(root)

		version = self.create_child(root, 'version')
		self.set_text(version, packet.version)

		headers = self.create_child(root, 'headers')
		for header in packet.headers:
			header_node = self.create_child(headers, 'header')
			self.create_text_node(header_node, 'name', header.header_name)
			must_understand = self.create_child(header_node, 'must-understand')
			self.set_text(must_understand, header.must_understand)
			self.create_value_node(header_node, header.value)

			self.complex_object_set = set()
			self.trait_set = set()

		messages = self.create_child(root, 'messages')
		for message in packet.messages:
			message_node = self.create_child(messages, 'message')
			self.create_text_node(message_node, 'target-uri', message.target_uri)
			self.create_text_node(message_node, 'response-uri', message.response_uri)
			self.create_value_node(message_node, message.value)

			self.complex_object_set = set()
			self.trait_set = set()


	##################################################

	def set_text(self, node, value):
		try:
			value = str(value)
		except UnicodeEncodeError:
			if type(value) == unicode:
				# keep it as unicode
				pass
			else:
				raise
		if len(value) > 40 and ('<' in value) and (']]>' not in value):
			# FIXME: how to reserve \r?
			text_node = self.doc.createCDATASection(value)
		else:
			text_node = self.doc.createTextNode(value)
		node.appendChild(text_node)

	def create_child(self, parent, tag):
		node = self.doc.createElement(tag)
		parent.appendChild(node)
		return node

	def create_text_node(self, parent, tag, value):
		node = self.create_child(parent, tag)
		self.set_text(node, str(value))
		return node

	##################################################
	def create_value_node(self, parent, value, tag = None):
		t = value.__class__
		funcs = {
				str          : self.create_str_node,
				unicode      : self.create_str_node,
				int          : self.create_int_node,
				float        : self.create_float_node,
				UNDEFINED    : self.create_undefined_node,
				NULL         : self.create_null_node,
				FALSE        : self.create_false_node,
				TRUE         : self.create_true_node,
				StrictArray  : self.create_strict_array_node,
				DateRef      : self.create_date_node,
				ObjectRef    : self.create_object_node,
				ArrayRef     : self.create_array_node,
				XMLRef       : self.create_xml_node,
				ByteArrayRef : self.create_byte_array_node,
				}
		assert funcs.has_key(t), 'Type %s is not supported' % t
		func = funcs[t]
		return func(parent, value, tag)

	def create_strict_array_node(self, parent, array, tag = None):
		assert isinstance(array, StrictArray)
		if tag == None:
			tag = 'strict-array'
		node = self.create_child(parent, tag)
		node.setAttribute('class', StrictArray.__name__)
		for i in array.array:
			self.create_value_node(node, i)
		return node

	def create_date_node(self, parent, dateref, tag = None):
		assert isinstance(dateref, DateRef)
		if tag == None:
			tag = 'float'
		date = dateref.date
		refindex = dateref.refindex

		node = self.create_child(parent, tag)
		node.setAttribute('class', date.__class__.__name__)
		node.setAttribute('id', str(refindex))
		self.set_text(node, date.double)
		return node

	def create_object_node(self, parent, objref, tag = None):
		assert isinstance(objref, ObjectRef)
		obj = objref.object
		refindex = objref.refindex
		if tag == None:
			tag = obj.__class__.__name__
		node = self.create_child(parent, tag)
		node.setAttribute('class', obj.__class__.__name__)
		node.setAttribute('id', str(refindex))
		if refindex in self.complex_object_set:
			# do nothing if referenced object has been defined somewhere
			pass
		else:
			self.complex_object_set.add(refindex)
			traitref = obj.trait
			trait = traitref.trait
			self.create_trait_node(node, traitref)

			if isinstance(trait, TraitExt):
				self.create_value_node(node, obj.members[0])
			elif isinstance(trait, StaticTrait):
				members_node = self.create_child(node, 'members')
				members = zip(trait.member_names, obj.members)
				for name, value in members:
					member_node = self.create_value_node(members_node, value, 'member')
					member_node.setAttribute('name', name)
			elif isinstance(trait, DynamicTrait):
				members_node = self.create_child(node, 'members')
				members = zip(trait.member_names, obj.members)
				for name, value in members:
					member_node = self.create_value_node(members_node, value, 'member')
					member_node.setAttribute('name', name)
				dynamic_members_node = self.create_child(node, 'dynamic-members')
				for name, value in obj.dynamic_members:
					member_node = self.create_value_node(dynamic_members_node, value, 'member')
					member_node.setAttribute('name', name)
			else:
				raise TypeError('Unkown trait type: %s' % trait.__class__)

		return node

	def create_trait_node(self, parent, traitref):
		assert isinstance(traitref, TraitRef)
		trait = traitref.trait
		refindex = traitref.refindex

		node = self.create_child(parent, trait.__class__.__name__)
		node.setAttribute('id', str(refindex))
		node.setAttribute('classname', trait.classname)
		if refindex in self.trait_set:
			# no nothing if the trait has been defined somewhere
			pass
		elif isinstance(trait, TraitExt):
			# don't need to display more if it's a trait-ext
			pass
		else:
			self.trait_set.add(refindex)
			for member_name in trait.member_names:
				member_node = self.create_child(node, 'member')
				member_node.setAttribute('name', member_name)
		return node

	def create_array_node(self, parent, arrayref, tag = None):
		assert isinstance(arrayref, ArrayRef)
		array = arrayref.array
		refindex = arrayref.refindex
		if tag == None:
			tag = array.__class__.__name__
		node = self.create_child(parent, tag)
		node.setAttribute('class', array.__class__.__name__)
		node.setAttribute('id', str(refindex))
		if refindex in self.complex_object_set:
			# no nothing if the array has been defined somewhere
			pass
		else:
			self.complex_object_set.add(refindex)
			list_node = self.create_child(node, 'list-items')
			for i in array.list:
				self.create_value_node(list_node, i)
			assoc_node = self.create_child(node, 'assoc-items')
			for k, v in array.assoc:
				item_node = self.create_value_node(assoc_node, v, 'item')
				item_node.setAttribute('key', k)
		return node

	def create_byte_array_node(self, parent, arrayref, tag = None):
		assert isinstance(arrayref, ByteArrayRef)
		array = arrayref.array
		refindex = arrayref.refindex
		if tag == None:
			tag = array.__class__.__name__
		node = self.create_child(parent, tag)
		node.setAttribute('class', array.__class__.__name__)
		node.setAttribute('id', str(refindex))
		if refindex in self.complex_object_set:
			# no nothing if the byte-array has been defined somewhere
			pass
		else:
			self.complex_object_set.add(refindex)
			data = array.content.encode('string_escape')
			node.setAttribute('length', str(len(data)))
			self.set_text(node, data)
		return node

	def create_xml_node(self, parent, xmlref, tag = None):
		assert isinstance(xmlref, XMLRef)
		xml_obj = xmlref.xml
		refindex = xmlref.refindex
		if tag == None:
			tag = xml_obj.__class__.__name__
		node = self.create_child(parent, tag)
		node.setAttribute('class', xml_obj.__class__.__name__)
		node.setAttribute('id', str(refindex))
		if refindex in self.complex_object_set:
			# no nothing if the xml has been defined somewhere
			pass
		else:
			self.complex_object_set.add(refindex)
			self.set_text(node, xml_obj.content)
			return node

	def create_str_node(self, parent, value, tag):
		if tag == None:
			tag = 'string'
		node = self.create_child(parent, tag)
		node.setAttribute('class', 'str')
		self.set_text(node, value)
		return node

	def create_int_node(self, parent, value, tag):
		if tag == None:
			tag = 'integer'
		node = self.create_child(parent, tag)
		node.setAttribute('class', 'int')
		self.set_text(node, value)
		return node

	def create_float_node(self, parent, value, tag):
		if tag == None:
			tag = 'float'
		node = self.create_child(parent, tag)
		node.setAttribute('class', 'float')
		self.set_text(node, value)
		return node

	def create_undefined_node(self, parent, value, tag):
		if tag == None:
			tag = 'undefined'
		node = self.create_child(parent, tag)
		node.setAttribute('class', 'undefined')
		return node

	def create_null_node(self, parent, value, tag):
		if tag == None:
			tag = 'null'
		node = self.create_child(parent, tag)
		node.setAttribute('class', 'null')
		return node

	def create_true_node(self, parent, value, tag):
		if tag == None:
			tag = 'boolean'
		node = self.create_child(parent, tag)
		node.setAttribute('class', 'true')
		return node

	def create_false_node(self, parent, value, tag):
		if tag == None:
			tag = 'boolean'
		node = self.create_child(parent, tag)
		node.setAttribute('class', 'false')
		return node

	##################################################

	def get_xml(self):
		assert self.doc != None, "Don't call get_xml twice"
		#TODO: clean the object
		pretty = self.doc.toprettyxml(indent="  ")
		self.doc.unlink()
		self.doc = None
		import re
		return re.sub(r'(<[^/][^<>]*[^/]>)\s*([^<>]{,40}?)\s*(</[^<>]*>)', r'\1\2\3', pretty)
# }}}
##################################################
# {{{ class FromXML
class FromXML:
	def __init__(self, xml):
		self.xml = xml

		self.complex_object_table = {}
		self.trait_table = {}

		self.from_xml()

	def from_xml(self):
		self.doc = minidom.parseString(self.xml.encode('utf-8'))
		doc = self.doc
		self.packet = AMFPacket()
		packet = self.packet

		root = doc.childNodes[0]
		version_node, headers_node, messages_node = self.get_children(root)

		packet.version = int(self.get_text(version_node))
		assert packet.version == 3

		for header_node in self.get_children(headers_node):
			header = HeaderType()
			name_node, must_understand_node, value_node = self.get_children(header_node)
			header.header_name = self.get_text(name_node)
			header.must_understand = bool(self.get_text(must_understand_node))
			header.value = self.get_value(value_node)
			packet.headers.append(header)

			self.complex_object_table = {}
			self.trait_table = {}
			
		for message_node in self.get_children(messages_node):
			message = MessageType()
			target_uri_node, response_uri_node, value_node = self.get_children(message_node)
			message.target_uri = self.get_text(target_uri_node)
			message.response_uri = self.get_text(response_uri_node)
			message.value = self.get_value(value_node)
			packet.messages.append(message)

			self.complex_object_table = {}
			self.trait_table = {}

	def get_children(self, node):
		return filter(lambda n: isinstance(n, minidom.Element), node.childNodes)

	def get_text(self, node):
		if node.firstChild:
			node = node.firstChild
			# XXX: why do I need to strip it?
			text = node.data.strip()
			if text == '':
				# FIXME: Not a good logical
				# FIXME: how to reserve \r?
				if isinstance(node.nextSibling, minidom.CDATASection):
					node = node.nextSibling
					text = node.data
		else:
			text = ''
		return text

	##################################################
	def get_value(self, node):
		class_type = node.getAttribute('class')
		funcs = {
				'str'           : self.get_str,
				'int'           : self.get_int,
				'float'         : self.get_float,
				'undefined'     : self.get_undefined,
				'null'          : self.get_null,
				'false'         : self.get_false,
				'true'          : self.get_true,
				'StrictArray'   : self.get_strict_array,
				'Date'          : self.get_date,
				'StaticObject'  : self.get_static_object,
				'DynamicObject' : self.get_dynamic_object,
				'ExtObject'     : self.get_ext_object,
				'Array'         : self.get_array,
				'ByteArray'     : self.get_byte_array,
				'XML'           : self.get_xml,
				}
		assert funcs.has_key(class_type), 'unkown class %s' % class_type
		func = funcs[class_type]
		return func(node)

	def get_str(self, node):
		return self.get_text(node)

	def get_int(self, node):
		return int(self.get_text(node))

	def get_float(self, node):
		return float(self.get_text(node))

	def get_undefined(self, node):
		return UNDEFINED()

	def get_null(self, node):
		return NULL()

	def get_false(self, node):
		return FALSE()

	def get_true(self, node):
		return TRUE()

	def get_strict_array(self, node):
		items = self.get_children(node)
		array = map(lambda n: self.get_value(n), items)
		return StrictArray(array)

	def get_static_object(self, node):
		refindex = int(node.getAttribute('id'))
		obj = self.get_referenced_object(node)
		if obj != None:
			return ObjectRef(obj, refindex)
		else:
			trait_node, members_node = self.get_children(node)
			trait = self.get_trait(trait_node)
			obj = StaticObject(trait)
			self.complex_object_table[refindex] = obj
			for member_node in self.get_children(members_node):
				obj.members.append(self.get_value(member_node))
			assert len(trait.get_member_names()) == len(obj.members)
			return ObjectRef(obj, refindex)

	def get_dynamic_object(self, node):
		refindex = int(node.getAttribute('id'))
		obj = self.get_referenced_object(node)
		if obj != None:
			return ObjectRef(obj, refindex)
		else:
			trait_node, members_node, dynamic_members_node = self.get_children(node)
			trait = self.get_trait(trait_node)
			obj = DynamicObject(trait)
			self.complex_object_table[refindex] = obj
			for member_node in self.get_children(members_node):
				obj.members.append(self.get_value(member_node))
			assert len(trait.get_member_names()) == len(obj.members)
			for dynamic_member_node in self.get_children(dynamic_members_node):
				name = dynamic_member_node.getAttribute('name')
				value = self.get_value(dynamic_member_node)
				obj.dynamic_members.append((name, value))
			return ObjectRef(obj, refindex)

	def get_ext_object(self, node):
		refindex = int(node.getAttribute('id'))
		obj = self.get_referenced_object(node)
		if obj != None:
			return ObjectRef(obj, refindex)
		else:
			trait_node, value_node = self.get_children(node)
			trait = self.get_trait(trait_node)
			obj = ExtObject(trait)
			self.complex_object_table[refindex] = obj
			obj.set_value(self.get_value(value_node))
			return ObjectRef(obj, refindex)

	def get_referenced_object(self, node):
		refindex = int(node.getAttribute('id'))
		if self.complex_object_table.has_key(refindex):
			obj = self.complex_object_table[refindex]
			assert obj.__class__.__name__ == node.nodeName
			return ObjectRef(obj, refindex)

	def get_trait(self, node):
		node_name = node.nodeName
		classname = node.getAttribute('classname')
		refindex = int(node.getAttribute('id'))
		if self.trait_table.has_key(refindex):
			trait = self.trait_table[refindex]
			assert trait.classname == classname
			assert trait.__class__.__name__ == node_name
			return TraitRef(trait, refindex)
		else:
			funcs = {
					'StaticTrait' : self.get_static_trait,
					'DynamicTrait' : self.get_dynamic_trait,
					'TraitExt' : self.get_ext_trait,
					}
			assert funcs.has_key(node_name), 'Unknown trait type: %s' % node_name
			return funcs[node_name](node)

	def get_static_trait(self, node):
		'Returns a new trait-ref of static-object'
		classname = node.getAttribute('classname')
		refindex = int(node.getAttribute('id'))
		trait = StaticTrait(classname)
		self.trait_table[refindex] = trait
		for member_name_node in self.get_children(node):
			trait.member_names.append(member_name_node.getAttribute('name'))
		return TraitRef(trait, refindex)

	def get_dynamic_trait(self, node):
		'Returns a new trait-ref of dynamic-object'
		classname = node.getAttribute('classname')
		refindex = int(node.getAttribute('id'))
		trait = DynamicTrait(classname)
		self.trait_table[refindex] = trait
		for member_name_node in self.get_children(node):
			trait.member_names.append(member_name_node.getAttribute('name'))
		return TraitRef(trait, refindex)

	def get_ext_trait(self, node):
		'Returns a new trait-ext-ref'
		classname = node.getAttribute('classname')
		refindex = int(node.getAttribute('id'))
		trait = TraitExt(classname)
		return TraitRef(trait, refindex)

	def get_array(self, node):
		refindex = int(node.getAttribute('id'))
		if self.complex_object_table.has_key(refindex):
			array = self.complex_object_table[refindex]
			return ArrayRef(array, refindex)
		else:
			list_node, assoc_node = self.get_children(node)
			array = Array()
			self.complex_object_table[refindex] = array
			for item in self.get_children(list_node):
				array.list.append(self.get_value(item))
			for item in self.get_children(assoc_node):
				name = item.getAttribute('key')
				value = self.get_value(item)
				array.assoc.append((name, value))
			return ArrayRef(array, refindex)

	def get_date(self, node):
		refindex = int(node.getAttribute('id'))
		if self.complex_object_table.has_key(refindex):
			date = self.complex_object_table[refindex]
			return DateRef(date, refindex)
		else:
			date = Date(float(self.get_text(node)))
			self.complex_object_table[refindex] = date
			return DateRef(date, refindex)

	def get_xml(self, node):
		refindex = int(node.getAttribute('id'))
		if self.complex_object_table.has_key(refindex):
			return ByteArrayRef(self.complex_object_table[refindex], refindex)
		else:
			xml_obj = XML(self.get_text(node))
			return XMLRef(xml_obj, refindex)

	def get_byte_array(self, node):
		refindex = int(node.getAttribute('id'))
		if self.complex_object_table.has_key(refindex):
			array = self.complex_object_table[refindex]
			return ByteArrayRef(array, refindex)
		else:
			array = ByteArray(self.get_text(node).decode('string_escape'))
			self.complex_object_table[refindex] = array
			return ByteArrayRef(array, refindex)

	##################################################
	def get_packet(self):
		assert self.packet != None, "Don't call get_packet twice"
		#TODO: clean the object
		packet = self.packet
		self.packet = None
		return packet

# }}}
##################################################

if __name__ == '__main__':
	from AMFDecoder import AMFDecoder
	fp = open('samples/login.txt', 'rb')
	fp = open('samples/login-response.txt', 'rb')
	fp = open('samples/client-ping.txt', 'rb')
	fp = open('samples/client-ping-response.txt', 'rb')
	fp = open('samples/7.txt', 'rb')
	fp = open('samples/9.txt', 'rb')
	decoder = AMFDecoder(fp)
	packet = decoder.decode()
	toxml = ToXML(packet)
	xml = toxml.get_xml()
	#print xml
	fromxml = FromXML(xml)
	#print fromxml.get_packet()


# vim: foldmethod=marker:
