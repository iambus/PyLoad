
import os
import os.path

class Project:
	def __init__(self, root):
		self.root = root
		self.records = []
		self.specials = []
		if not os.path.exists(self.root):
			os.makedirs(self.root)
		os.path.isdir(self.root)

		self.global_factory = None
		self.user_factory = None
		self.iteration_factory = None
	
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

