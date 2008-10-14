
from Project import Project

def load_project(path):
	project = Project()
	project.load(path)
	return project

def save_project(project, path):
	project.save(path)

def play_project(project):
	raise NotImplementedError()

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

	clean_project_in_path('a.pkl')

if __name__ == '__main__':
	#main()
	test()

