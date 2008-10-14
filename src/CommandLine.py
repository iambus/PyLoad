
from Project import Project

def load_project(path):
	project = Project()
	project.load(path)
	return project

def save_project(project, path):
	project.save(path)

#FIXME: dirty and duplicated code
def play_project(project, reporter = None):
	assert isinstance(project, Project)

	if project.current_special == None:
		raise RuntimeError('No special to start!')

	user_count = project.user_count
	iteration_count = project.iteration_count
	special = project.current_special
	user_factory = project.user_factory
	iteration_factory = project.iteration_factory
	global_factory = project.global_factory

	from Report import Report
	if type(reporter) in (str, unicode):
		reporter = Report(reporter)
	if reporter != None:
		assert isinstance(reporter, Report)

		import datetime
		start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		summary = 'Start Time: %s\nUser Count: %s\nIteration Count: %s\nSpecial: %s' % (start_time, user_count, iteration_count, special.label)

		import ReportManager
		ReportManager.start_report(reporter = reporter, project = project, summary = summary)

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
	sys.path.append('runtime')
	sys.path.append('plugin')

	policy.play()

	if len(sys.path) >= 2 and sys.path[-2:] == ['runtime', 'plugin']:
		sys.path.pop()
		sys.path.pop()

	if reporter:
		reporter.finish()

def clone_project(project):
	data = project.repository_internal
	project.repository_internal = None

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

def read_report(path):
	raise NotImplementedError()

def main():
	raise NotImplementedError()

def test():
#	project = Project()
#	project.load_as_global('b.pkl')
#	import Repository
#	Repository.trace_classes()

	project = load_project('workflow.pkl')
	project.user_count = 3
	play_project(project, 'b-report.db')

if __name__ == '__main__':
	#main()
	test()

