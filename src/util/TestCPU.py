
import unittest

import cpu

class TestTextExtract(unittest.TestCase):
	def setUp(self):
		pass

	def assertEtract(self, raw, expected):
		got = cpu.extract_from_text(raw)
		self.assertEqual(got, expected)

	def testBasic(self):
		raw = '''1230731249.55:1230731252.54:12.21'''
		self.assertEtract(raw, [
				[1230731249.55, 1230731252.54, 12.21]
			])

	def testBlankInline(self):
		raw = '''1230731249.55:1230731252.54:   12.21'''
		self.assertEtract(raw, [
				[1230731249.55, 1230731252.54, 12.21]
			])

	def testBlankOutline(self):
		raw = '''
		1230731249.55:1230731252.54:   12.21
		'''
		self.assertEtract(raw, [
				[1230731249.55, 1230731252.54, 12.21]
			])

	def testCommentOutline(self):
		raw = '''
		1230731249.55:\t1230731252.54:   12.21 # comment
		'''
		self.assertEtract(raw, [
				[1230731249.55, 1230731252.54, 12.21]
			])

	def testCommentInline(self):
		raw = '''
		# 
		# 1230731249.55:1230731252.54:   12.21
		1230731249.55:1230731252.54:   12.21
     		\t   
		'''
		self.assertEtract(raw, [
				[1230731249.55, 1230731252.54, 12.21]
			])

	def testPercentSignInline(self):
		raw = '''
		1230731249.55:1230731252.54:   12.21%
		'''
		self.assertEtract(raw, [
				[1230731249.55, 1230731252.54, 12.21]
			])

if __name__ == '__main__':
	unittest.main()

