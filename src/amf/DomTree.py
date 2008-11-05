
from SimpleXMLTree import IXMLTree

from xml.dom import minidom

class DomTree(IXMLTree):
	def __init__(self, tag = None):
		IXMLTree.__init__(self, tag)

	def init_root(self, tag):
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
		tree = cls()
		tree.doc = minidom.parseString(text.encode('utf-8'))
		tree.root = tree.doc.childNodes[0]
		return tree


