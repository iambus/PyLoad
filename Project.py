
import os
import os.path

class Project:
	def __init__(self, root):
		self.root = root
		self.records = []
		if not os.path.exists(self.root):
			os.makedirs(self.root)
		os.path.isdir(self.root)
	
	def add_record(self, record):
		self.records.append(record)
		record.rootdir = self.root

	def save(self):
		pass
	
	def load(self):
		pass



