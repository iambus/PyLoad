
class IXMLTree:
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


