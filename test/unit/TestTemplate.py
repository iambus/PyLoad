
import unittest
import LoadTestEnv

import Template

class TestTemplate(unittest.TestCase):
	def setUp(self):
		self.variables = {'x':1, 'y':'hello', 'z':{1:2, 3:4}}

	def testEscape(self):
		self.assertEqual(Template.escape('x'), 'x')
		self.assertEqual(Template.escape('$x'), '$$x')
		self.assertEqual(Template.escape('$$x'), '$$$$x')
		self.assertEqual(Template.escape('${x}'), '$${x}')

	def testSubst(self):
		self.assertSubst('x', 'x')
		self.assertSubst('$', '$')
		self.assertSubst('$$', '$')
		self.assertSubst('$x', '1')
		self.assertSubst('${x}', '1')
		self.assertSubst('$$$x', '$1')
		self.assertSubst('$$$$x', '$$x')
		self.assertSubst('a$xb', 'a$xb')
		self.assertSubst('a${x}b', 'a1b')
		self.assertSubst('${x+y}', '${x+y}')
	
	def testEval(self):
		#TODO: not impelemented eval
		pass

	def testUnicode(self):
		self.assertEqual(Template.escape('x'), u'x')
		self.assertEqual(Template.escape(u'x'), 'x')
		self.assertEqual(Template.escape(u'x'), u'x')

		self.assertEqual(Template.escape('$x'), u'$$x')
		self.assertEqual(Template.escape(u'$x'), '$$x')
		self.assertEqual(Template.escape(u'$x'), u'$$x')

		variables = {'x':u'1', u'y':'2', u'z':u'3'}
		self.assertEqual(Template.subst('$x', variables), '1')
		self.assertEqual(Template.subst('$y', variables), '2')
		self.assertEqual(Template.subst('$z', variables), '3')

		self.assertEqual(Template.subst(u'$x', variables), '1')
		self.assertEqual(Template.subst(u'$y', variables), '2')
		self.assertEqual(Template.subst(u'$z', variables), '3')

		self.assertEqual(Template.subst('$x', variables), u'1')
		self.assertEqual(Template.subst('$y', variables), u'2')
		self.assertEqual(Template.subst('$z', variables), u'3')

		self.assertEqual(Template.subst(u'$x', variables), u'1')
		self.assertEqual(Template.subst(u'$y', variables), u'2')
		self.assertEqual(Template.subst(u'$z', variables), u'3')


	def assertSubst(self, source, target):
		self.assertEqual(Template.subst(source, self.variables), target)

if __name__ == '__main__':
	unittest.main()

