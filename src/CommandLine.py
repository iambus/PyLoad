

##################################################

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

	if reporter != None:
		from Report import Report
		if type(reporter) in (str, unicode):
			reporter = Report(reporter)
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

##################################################

def read_report(path):
	raise NotImplementedError()

##################################################

def show_classes(project):
	import Repository
	Repository.trace_classes(project.repository_internal)

##################################################

def main():
	import sys
	run_command(sys.argv[1:])

def run_command(argv):
	import getopt, sys

	if not argv:
		usage()
		sys.exit(2)

	try:
		optlist, args = getopt.getopt(argv, 'hp:r:cu:i:o:', [
				'help',
				'project=',
				'report=',
				'clean',
				'user=',
				'iteration=',
				'host=',
				'operation=',
				'show-classes', # for debug
			])
		optdict = dict(optlist)
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	project_path = None
	report_path = None
	if_clean = False
	user_count = None
	iteration_count = None
	host = None
	operation = None

	if_show_classes = False

	for o, a in optlist:
		if o in ('-h', '--help'):
			usage()
			sys.exit(2)
		elif o in ('-p', '--project'):
			project_path = a
		elif o in ('-r', '--report'):
			report_path = a
		elif o in ('-c', '--clean'):
			if_clean = True
			if operation == None:
				operation = 'clean'
		elif o in ('-u', '--user'):
			user_count = int(a)
		elif o in ('-i', '--iteration'):
			iteration_count = int(a)
		elif o in ('--host'):
			host = a
		elif o in ('-o', '--operation'):
			operation = a
			if operation not in ('clean', 'play', 'report'):
				sys.exit('Unknown operation %s. Only clean, play, and report are supported now.' % operation)
		elif o in ('--show-classes'):
			if_show_classes = True
			if operation == None:
				operation = 'show-classes'
		else:
			sys.exit('Unknown option %s' % o)

	if operation == None:
		operation = 'play'

	if operation == 'report':
		if report_path == None:
			if args:
				report_path = args.pop(0)
			else:
				sys.exit('Report path must be specified by option -r or --report=')
		read_report(report_path)
		sys.exit()

	if project_path == None:
		if args:
			project_path = args.pop(0)
		else:
			sys.exit('Project path must be specified by option -p or --project=')

	if args:
		sys.exit('More arguments than expected: %s' % args)

	if if_clean or operation == 'clean':
		clean_project_in_path(project_path)
		if operation == 'clean':
			sys.exit()

	project = load_project(project_path)

	if if_show_classes or operation == 'show-classes':
		show_classes(project)

	if operation in ('show-classes'):
		sys.exit()

	assert operation == 'play', 'Unknown operation: %s. (Should not happen here.)' % operation

	if user_count != None:
		project.user_count = user_count
	if iteration_count != None:
		project.iteration_count = iteration_count
	if host != None:
		for record in project.records:
			record.set_host(host)

	play_project(project, report_path)


def usage():
	print '''  -h, --help         display this help and exit
  -p, --project      specify the project file path
  -r, --report       specify the report file path (to save, or to read)
  -c, --clean        remove unused object in project file
  -u, --user         specify the user numbers to play
  -i, --iteration    specify the iteration numbers to play
	  --host         specify the server host:port. E.g. localhost:8000
  -o, --operation    should be 'play' (default value), 'clean', or 'report'.
      --show-classes show classes of objects used in project

  Examples:
  1. To play a project:
     python CommandLine.py project-name.pkl
  2. To play a project with user numbers = 10, and iteration numbers = 2:
     python CommandLine.py -u 10 -i 2 project-name.pkl
  3. To play a project, and save report to file system:
     python CommandLine.py -p project-name.pkl -r report-name.db
  4. To clean useless objects in a project (this makes project file smaller):
     python CommandLine.py -c project-name.pkl
  5. To show class usages in a project (for debug purpose):
     python CommandLine.py --show-classes project-name.pkl
  6. To display help:
     python CommandLine.py -h'''

##################################################

def test():
#	project = Project()
#	project.load_as_global('b.pkl')
#	import Repository
#	Repository.trace_classes()

	project = load_project('workflow.pkl')
	project.user_count = 3
	project.iteration_count = 10
	#play_project(project, 'b-report.db')
	play_project(project)

##################################################

if __name__ == '__main__':
	main()

