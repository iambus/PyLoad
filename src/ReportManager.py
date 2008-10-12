
import Report
import Project
import Record

def start_report(reporter, project, summary = ''):
	hits = {}
	def loop_all(node):
		if isinstance(node, Record.Hit):
			hits[node.uuid] = (node.uuid, node.label, node.url)
		elif hasattr(node, 'childern'):
			for c in node.childern:
				loop_all(c)
	for s in project.specials:
		loop_all(s)

	reporter.start(hits = hits.values(), summary = summary)

