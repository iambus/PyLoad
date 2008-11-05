
##################################################

# {{{ Interface IXML
class IXML:
	def __init__(self, tag = None):
		if tag != None:
			self.init_root(tag)

	def init_root(self, tag):
		raise NotImplementedError()

	def get_root_node(self):
		raise NotImplementedError()

	def create_child(self, parent, tag):
		raise NotImplementedError()

	def get_childern(self, parent):
		raise NotImplementedError()

	def set_text(self, node, value):
		raise NotImplementedError()

	def get_text(self, node):
		raise NotImplementedError()

	def set_attribute(self, node, name, value):
		raise NotImplementedError()

	def get_attribute(self, node, name):
		raise NotImplementedError()

	def get_tag(self, node):
		raise NotImplementedError()

	def tostring(self):
		raise NotImplementedError()

	@classmethod
	def fromstring(cls, text):
		raise NotImplementedError()

	# Help methods
	def create_text_node(self, parent, tag, value):
		node = self.create_child(parent, tag)
		self.set_text(node, str(value))
		return node

	# TODO: bad API
	def unlink(self):
		raise NotImplementedError()
# }}}

##################################################

# {{{ minidom implementation
class DomXML(IXML):
	def __init__(self, tag = None):
		IXML.__init__(self, tag)

	def init_root(self, tag):
		from xml.dom import minidom
		self.doc = minidom.Document()
		self.root = self.doc.createElement(tag)
		self.doc.appendChild(self.root)
		return self.root

	def get_root_node(self):
		return self.root

	def create_child(self, parent, tag):
		node = self.doc.createElement(tag)
		parent.appendChild(node)
		return node

	def get_childern(self, node):
		from xml.dom import minidom
		return filter(lambda n: isinstance(n, minidom.Element), node.childNodes)

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

	def get_text(self, node):
		if node.firstChild:
			node = node.firstChild
			# XXX: why do I need to strip it?
			text = node.data.strip()
			if text == '':
				# FIXME: Not a good logical
				# FIXME: how to reserve \r?
				from xml.dom import minidom
				if isinstance(node.nextSibling, minidom.CDATASection):
					node = node.nextSibling
					text = node.data
		else:
			text = ''
		return text

	def set_attribute(self, node, name, value):
		node.setAttribute(name, value)

	def get_attribute(self, node, name):
		return node.getAttribute(name)

	def get_tag(self, node):
		return node.nodeName

	def tostring(self):
		assert self.doc != None, "Don't call tostring twice"
		#TODO: clean the object
		pretty = self.doc.toprettyxml(indent="  ")
		self.doc.unlink()
		self.doc = None
		import re
		return re.sub(r'(<[^/][^<>]*[^/]>)\s*([^<>]{,40}?)\s*(</[^<>]*>)', r'\1\2\3', pretty)

	@classmethod
	def fromstring(cls, text):
		from xml.dom import minidom
		tree = DomXML()
		tree.doc = minidom.parseString(text.encode('utf-8'))
		tree.root = tree.doc.childNodes[0]
		return tree
# }}}

##################################################

# {{{ lxml implementation
class LXML(IXML):
	def __init__(self, tag = None):
		IXML.__init__(self, tag)

	def init_root(self, tag):
		from lxml import etree
		self.root = etree.Element(tag)
		return self.root

	def get_root_node(self):
		return self.root

	def create_child(self, parent, tag):
		from lxml import etree
		return etree.SubElement(parent, tag)

	def get_childern(self, node):
		return list(node)

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
			from lxml import etree
			node.text = etree.CDATA(value)
		else:
			node.text = value

	def get_text(self, node):
		text = node.text
		if node.text == None:
			text = ''
		return text

	def set_attribute(self, node, name, value):
		node.set(name, value)

	def get_attribute(self, node, name):
		return node.get(name)

	def get_tag(self, node):
		return node.tag

	def tostring(self):
		from lxml import etree
		pretty = etree.tostring(self.root, pretty_print=True)

		#TODO: clean the object

		import re
		return re.sub(r'(<[^/][^<>]*[^/]>)\s*([^<>]{,40}?)\s*(</[^<>]*>)', r'\1\2\3', pretty)

	@classmethod
	def fromstring(cls, text):
		tree = cls()

		from lxml import etree
		# XXX: encoding?
		tree.root = etree.fromstring(text)

		return tree
# }}}

# vim: foldmethod=marker:
