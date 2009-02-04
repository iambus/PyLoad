
import pickle
import os
import os.path
import Repository

##################################################

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

	def raw_save(self, path):
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

	def clean_save(self, path):
		new_project = clone_project(self)
		new_project.raw_save(path)

	save = clean_save
	
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

##################################################
# Help functions, mainly for CommandLine usage

def load_project(path):
	project = Project()
	project.load(path)
	return project

def save_project(project, path):
	project.raw_save(path)

#FIXME: dirty and duplicated code
def play_project(project, reporter = None, project_path = 'unkown'):
	assert isinstance(project, Project)

	if project.current_special == None:
		raise RuntimeError('No special to start!')

	user_count = project.user_count
	iteration_count = project.iteration_count
	special = project.current_special
	user_factory = project.user_factory
	iteration_factory = project.iteration_factory
	global_factory = project.global_factory

	if reporter != None:
		from Report import Report
		if type(reporter) in (str, unicode):
			reporter = Report(reporter)
		assert isinstance(reporter, Report)

		import datetime
		start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		info = {
				'Start Time': start_time,
				'User Count': user_count,
				'Iteration Count': iteration_count,
				'Special': special.label,
				'Project Path': project_path,
			}

		import ReportManager
		ReportManager.start_report(reporter = reporter, project = project, info = info)

	import PlayPolicy
	policy = PlayPolicy.IterationBasedPlayPolicy(
			player = special,
			user_count = user_count,
			iteration_count = iteration_count,
			user_factory = user_factory,
			iteration_factory = iteration_factory,
			global_factory = global_factory,
			reporter = reporter
			)

	import sys
	sys.path.append(os.path.join(sys.path[0], 'runtime'))
	sys.path.append(os.path.join(sys.path[0], 'plugin'))

	policy.play()

	if len(sys.path) >= 2 and sys.path[-2:] == ['runtime', 'plugin']:
		sys.path.pop()
		sys.path.pop()

	if reporter:
		reporter.finish()

def clone_project(project):
	data = project.repository_internal
	project.repository_internal = None #FIXME: should not modify source project

	import Repository
	new_data = Repository.RepositoryInternal()
	import Clone
	new_project = Clone.clone(project, Repository.LocalRepository(new_data))

	project.repository_internal = data
	new_project.repository_internal = new_data

	return new_project

def clean_project(project):
	raise NotImplementedError()

def clean_project_in_path(path):
	project = load_project(path)
	new_project = clone_project(project)
	save_project(new_project, path)

##################################################

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



