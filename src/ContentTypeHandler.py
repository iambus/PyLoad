
import re
import Coder
import Validator


class ContentType:
	@property
	def type(self):
		raise NotImplementedError()

	@property
	def coder(self):
		return Coder.EmptyCoder

	@property
	def syntax(self):
		import editor.syntax.default
		return editor.syntax.default

	@property
	def validator(self):
		return Validator.DefaultResponseValidator

class DefaultContentType(ContentType):
	@property
	def type(self):
		return 'default'

class HTMLContentType(ContentType):
	@property
	def type(self):
		return 'html'

	@property
	def syntax(self):
		import editor.syntax.html
		return editor.syntax.html

class XMLContentType(ContentType):
	@property
	def type(self):
		return 'xml'

	@property
	def syntax(self):
		import editor.syntax.xml
		return editor.syntax.xml

class AMFContentType(ContentType):
	@property
	def type(self):
		return 'amf'

	@property
	def coder(self):
		return Coder.AMFCoder

	@property
	def syntax(self):
		import editor.syntax.xml
		return editor.syntax.xml

	@property
	def validator(self):
		return Validator.AMFResponseValidator

class PythonContentType(ContentType):
	@property
	def type(self):
		return 'python'

	@property
	def syntax(self):
		import editor.syntax.python
		return editor.syntax.python


class BinContentType(ContentType):
	@property
	def type(self):
		return 'bin'

	@property
	def coder(self):
		return Coder.BinCoder


# TODO: Keep ContentTypeHandler for compatibility reason. Remove it in future
# immutable: dirty hack
# XXX: how to implement an immutable instance in Python?
class ContentTypeHandler(tuple):
	def __new__(self, coder = Coder.EmptyCoder, syntax = None, validator = Validator.DefaultResponseValidator):
		if syntax == None:
			import editor.syntax.default
			syntax = editor.syntax.default
		from editor.Syntax import Syntax
		return tuple.__new__(self, (coder, Syntax(syntax), validator))


	def __getattr__(self, name):
		if name == 'coder':
			return self[0]
		if name == 'syntax':
			return self[1]
		if name == 'validator':
			return self[2]
		raise AttributeError("No attribute "+name)

	def __setattr__(self, name, v):
		raise AttributeError("ContentTypeHandler is immutable")

	#FIXME: maybe not good enough...
	def __deepcopy__(self, ignored):
		return ContentTypeHandler(self.coder, self.syntax, self.validator)


mapping = {
		'default' : DefaultContentType(),
		'html' : HTMLContentType(),
		'xml' : XMLContentType(),
		'amf' : AMFContentType(),
		'python' : PythonContentType(),
		'bin' : BinContentType(),
		}


def get_handler(content):

	m = re.search(r'^content-type:\s*([^\r\n]*)', content, re.I|re.M)
	if m:
		type = m.group(1)
		if   re.search(r'application/x-amf', type, re.I):
			return mapping['amf']
		elif re.search(r'xml', type, re.I):
			return mapping['xml']
		elif re.search(r'html', type, re.I):
			return mapping['html']
		elif re.search(r'text', type, re.I):
			return mapping['default']
		elif re.search(r'application/octet-stream', type, re.I):
			return mapping['bin']
		elif re.search(r'multipart', type, re.I):
			return mapping['bin']
		else:
			return mapping['default']
	return ContentTypeHandler()

if __name__ == '__main__':
	h = ContentTypeHandler()

