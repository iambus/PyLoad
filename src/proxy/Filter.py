
'''
A rule return True value if the rule matched.
A filter return True value if the applied input should be ignored.
'''

import re

class RegexRule:
	def __init__(self, regexp):
		self.regexp = re.compile(regexp)

	def test(self, input):
		return self.regexp.match(input)

class EmptyFilter:
	def test(self, input):
		pass

class RuleFilter:
	def __init__(self, conf_path):
		try:
			fp = open(conf_path)
			self.rules = map(RegexRule, [line.strip() for line in fp])
			fp.close()
		except Exception, e:
			self.rules = []
			print e
	def test(self, input):
		for rule in self.rules:
			if rule.test(input):
				return True

class ContentFilter:
	def __init__(self, types):
		self.types = types
		self.type_re = re.compile(r'|'.join(map(re.escape, types)), re.I)
		self.content_type_re = re.compile(r'^content-type:\s*(.*)', re.I|re.M)

	def has_correct_content_type(self, input):
		assert isinstance(input, basestring)
		m = self.content_type_re.search(input)
		if m:
			content_type = m.group(1)
			return self.type_re.search(content_type)

	def test(self, input):
		return not self.has_correct_content_type(input)

class DefaultContentFilter(ContentFilter):
	def __init__(self):
		ContentFilter.__init__(self, ['text', 'html', 'xml', 'application/x-amf'])

if __name__ == '__main__':
	filter = Filter('blocks.txt')
	print filter.test('https')

