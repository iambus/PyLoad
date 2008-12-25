
import Report
import Project
import Record

def start_report(reporter, project, info = ()):
	hits = {}
	pages = {}
	def loop_all(node):
		if isinstance(node, Record.Page):
			pages[node.uuid] = (node.uuid, node.label, map(lambda h: h.uuid, node.hits))
		if isinstance(node, Record.Hit):
			hits[node.uuid] = (node.uuid, node.label, node.url)
		elif hasattr(node, 'childern'):
			for c in node.childern:
				loop_all(c)
	for s in project.specials:
		loop_all(s)

	reporter.start(hits = hits.values(), pages = pages.values(), info = info)

