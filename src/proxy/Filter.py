
'''
A rule return True value if the rule matched.
A filter return True value if the applied input should be ignored.
'''

import re

def find_block_list():
	import sys
	import os.path
	search_path = ['.']
	search_path.extend(sys.path)
	search_path.insert(2, os.path.join(sys.path[0], 'proxy'))
	for path in search_path:
		filepath = os.path.join(path, 'block.txt')
		if os.path.isfile(filepath):
			fp = open(filepath)
			try:
				return filter(lambda line: line, [line.strip() for line in fp])
			finally:
				fp.close()
	else:
		return []

class RegexRule:
	def __init__(self, regexp):
		self.regexp = re.compile(regexp)

	def test(self, input):
		return self.regexp.search(input)

class EmptyFilter:
	''' An empty filter keeps everything '''
	def test(self, input):
		pass

class RuleFilter:
	def __init__(self, lines):
		self.rules = map(RegexRule, [line.strip() for line in lines])
	def test(self, input):
		for rule in self.rules:
			if rule.test(input):
				return True

class DefaultRuleFilter(RuleFilter):
	def __init__(self):
		RuleFilter.__init__(self, find_block_list())

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
	print find_block_list()
	filter = DefaultRuleFilter()
	#print filter.test('https')

