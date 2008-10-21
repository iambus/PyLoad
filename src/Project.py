
import pickle
import os
import os.path
import Repository

class Project:
	def __init__(self):
		self.records = []
		self.specials = []

		self.global_factory = None
		self.user_factory = None
		self.iteration_factory = None

		self.user_count = 1
		self.iteration_count = 1
		self.current_special = None

		self.repository_internal = Repository.get_global_repository().data

	def add_record(self, record):
		self.records.append(record)

	def remove_record(self, record):
		self.records.remove(record)

	def add_special(self, special):
		self.specials.append(special)

	def remove_special(self, special):
		self.specials.remove(special)

	def save(self, path):
		output = open(path, 'wb')
		try:
			pickle.dump(self, output)
		except Exception, e:
			print '--------------------------------------------------'
			print '---------- Exception during pickle.dump ----------'
			print e
			print '---------- Try to dump in small pieces -----------'
			def testDump(data, name):
				print '-------------- Dumping %s... ----------------' % name
				from cStringIO import StringIO
				o = StringIO()
				try:
					pickle.dump(data, o)
					print 'Dump %s successfully' % name
				except:
					print 'Dump %s error %s' % (name, e)
				finally:
					o.close()
			testDump(self.records, 'records')
			testDump(self.specials, 'specials')
			testDump(self.current_special, 'current-special')
			testDump(self.global_factory, 'global-factory')
			testDump(self.user_factory, 'user-factory')
			testDump(self.iteration_factory, 'iteration-factory')
			testDump(self.repository_internal, 'repository-internal')
			print '--------------------------------------------------'
			raise
		finally:
			output.close()
	
	def load(self, path):
		input = open(path, 'rb')
		try:
			p = pickle.load(input)
			self.records = p.records
			self.specials = p.specials
			self.global_factory = p.global_factory
			self.user_factory = p.user_factory
			self.iteration_factory = p.iteration_factory
			self.user_count = p.user_count
			self.iteration_count = p.iteration_count
			self.current_special = p.current_special
			self.repository_internal = p.repository_internal

		finally:
			input.close()

	def load_as_global(self, path):
		self.load(path)
		Repository.get_global_repository().data = self.repository_internal

class NoneProject:
	def __init__(self, root = None):
		self.records = []
		self.specials = []
	def add_record(self, record):
		self.records.append(record)
	def remove_record(self, record):
		self.records.remove(record)
	def add_special(self, special):
		self.specials.append(special)
	def remove_special(self, special):
		self.specials.remove(special)
	def save(self):
		pass
	def load(self):
		pass

if __name__ == '__main__':
	import pickle
	import Player
	import Record
	p = Project()

	p.add_record(Player.Script('print 2'))
	p.add_record(Record.Hit(''))
	p.save('.load/project.pkl')

	p.records = []

	p.load_as_global('.load/project.pkl')
	print p.records[0].uuid

	Repository.lookup(p.records[0].uuid)



