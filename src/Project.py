
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



