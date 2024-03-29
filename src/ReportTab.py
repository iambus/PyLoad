
import wx
import LineChartPanel

class ReportDropTarget(wx.FileDropTarget):
	def __init__(self, callback):
		wx.FileDropTarget.__init__(self)
		self.callback = callback

	def OnDropFiles(self, x, y, filenames):
		assert len(filenames) == 1, 'Please drop one and only one file'
		self.callback(filenames[0])


class ReportData:

	def connect(self, path):
		import os.path
		if not os.path.isfile(path):
			raise RuntimeError("%s doesn't exist" % path)

		import sqlite3

		if type(path) == str:
			try:
				path = path.decode()
			except UnicodeDecodeError:
				import sys
				path = path.decode(sys.getfilesystemencoding())
		assert type(path) == unicode
		path = path.encode('utf-8')

		connection = sqlite3.connect(path)

		return connection

	def load_data(self, cursor):

		# hit summary
		cursor.execute('select id, label, avg, max, min, count from summary')
		self.hit_summary = [row for row in cursor]

		# hit data
		cursor.execute('select hitid, start, end from hits')
		self.raw_hits = [row for row in cursor]
		self.raw_hits.sort()

		self.hit_data = [ (hitid, (start + end) / 2, end - start) for hitid, start, end in self.raw_hits]
		self.hit_data.sort()

		self.hit_data_by_start_time = [ (hitid, start, end - start) for hitid, start, end in self.raw_hits]
#		self.hit_data_by_start_time.sort()
		self.hit_data_by_end_time = [ (hitid, end, end - start) for hitid, start, end in self.raw_hits]
		self.hit_data_by_end_time.sort()

		self.hit_datas = [self.hit_data_by_start_time, self.hit_data, self.hit_data_by_end_time]

		# page summary
		cursor.execute('select id, label, avg, max, min, count from page_summary')
		self.page_summary = [row for row in cursor]

		# page data
		cursor.execute('select pageid, start, end, response_time from pages')
		self.raw_pages = [row for row in cursor]
		self.raw_pages.sort()
		
		self.page_data = [ (pageid, (start + end) / 2, response_time) for pageid, start, end, response_time in self.raw_pages ]
		self.page_data.sort()

		self.page_data_by_start_time = [ (pageid, start, response_time) for pageid, start, end, response_time in self.raw_pages ]
#		self.page_data_by_start_time.sort()
		self.page_data_by_end_time = [ (pageid, end, response_time) for pageid, start, end, response_time in self.raw_pages ]
		self.page_data_by_end_time.sort()

		self.page_datas = [self.page_data_by_start_time, self.page_data, self.page_data_by_end_time]

		# errors data
		cursor.execute('select id, count from error_summary')
		self.errors = dict([row for row in cursor])


			
	def __init__(self, path):

		connection = self.connect(path)
		cursor = connection.cursor()

		try:
			self.load_data(cursor)
		finally:
			cursor.close()
			connection.close()


class ReportTab(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.splitter = wx.SplitterWindow(self, style=wx.BORDER_NONE)

		self.list = wx.ListCtrl(self.splitter, -1,
				style=wx.LC_REPORT
				#| wx.BORDER_SUNKEN
				#| wx.BORDER_NONE
				#| wx.LC_EDIT_LABELS
				#| wx.LC_SORT_ASCENDING
				#| wx.LC_NO_HEADER
				#| wx.LC_VRULES
				#| wx.LC_HRULES
				| wx.LC_SINGLE_SEL
				)
		self.list.InsertColumn(0, "ID")
		self.list.InsertColumn(1, "Label")
		self.list.InsertColumn(2, "Avg")
		self.list.InsertColumn(3, "Max")
		self.list.InsertColumn(4, "Min")
		self.list.InsertColumn(5, "Count")
		self.list.InsertColumn(6, "Error")

		self.list.SetColumnWidth(0, 60)
		self.list.SetColumnWidth(1, 60)
		self.list.SetColumnWidth(2, 60)
		self.list.SetColumnWidth(3, 60)
		self.list.SetColumnWidth(4, 60)
		self.list.SetColumnWidth(5, 60)
		self.list.SetColumnWidth(6, 60)


		self.chartPanel = LineChartPanel.LineChart(self.splitter)
		self.chartPanel.xformat = LineChartPanel.XTimeFormatter
		self.chartPanel.yformat = LineChartPanel.YMSFormatter

		self.splitter.SplitHorizontally(self.list, self.chartPanel, 180)

		import Layout
		Layout.SingleLayout(self, self.splitter)

		self.SetDropTarget(ReportDropTarget(self.LoadReport))


		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)

		self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnSwitch, self.list)

		self.chartPanel.Bind(wx.EVT_MIDDLE_UP, self.OnSwitchTime, self.chartPanel)

	def LoadReport(self, path):
		# FIXME: refacotr here
		data = ReportData(path)
		# mix it in
		for attr in dir(data):
			if not attr.startswith('_'):
				setattr(self, attr, getattr(data, attr))

		
		self.data_index = 1

		self.datas = [data.hit_datas, data.page_datas]
		self.type_index = 0

		self.ShowHits()

	def ShowPages(self):
		self.summary = self.page_summary
		self.data = self.page_datas[self.data_index]
		self.LoadSummary(self.page_summary)

		h = wx.ListItem()
		h.SetText('PageID')
		self.list.SetColumn(0, h)

		self.chartPanel.Clear()

	def ShowHits(self):
		self.summary = self.hit_summary
		self.data = self.hit_datas[self.data_index]
		self.LoadSummary(self.hit_summary)

		h = wx.ListItem()
		h.SetText('ID')
		self.list.SetColumn(0, h)

		self.chartPanel.Clear()

	def LoadSummary(self, rows):
		self.list.DeleteAllItems()
		def tostr(v):
			if type(v) in [str, unicode]:
				return v
			elif type(v) in [float]:
				return str(int(v))
			else:
				return str(v)

		for i in range(len(rows)):
			row = rows[i]
			row = map(tostr, row)
			index = self.list.InsertStringItem(i, row[0])
			self.list.SetStringItem(index, 1, row[1])
			self.list.SetStringItem(index, 2, row[2])
			self.list.SetStringItem(index, 3, row[3])
			self.list.SetStringItem(index, 4, row[4])
			self.list.SetStringItem(index, 5, row[5])
			self.list.SetStringItem(index, 6, str(self.errors.get(row[0], '-')))

		if len(rows):
			self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
			if self.list.GetColumnWidth(1) < 60:
				self.list.SetColumnWidth(1, 60)

	def LoadChart(self, uid):
		data = [d[1:3] for d in self.data if d[0] == uid]
		self.chartPanel.SetData(data)

	# XXX: why I need this?
	def ResetSize(self):
		self.splitter.SetSashPosition(120)

	def OnItemSelected(self, event):
		uid = self.list.GetItemText(event.m_itemIndex)
		self.LoadChart(uid)

	def OnSwitch(self, event):
		if event.Column == -1:
			self.type_index = (self.type_index + 1) % 2
			if self.type_index == 0 or self.hit_data == self.page_data:
				self.ShowHits()
			else:
				self.ShowPages()

	def OnSwitchTime(self, event):
		self.data_index = (self.data_index + 1) % 3
		if self.type_index == 0 or self.hit_data == self.page_data:
			self.data = self.hit_datas[self.data_index]
		else:
			self.data = self.page_datas[self.data_index]

		uid = self.GetSelectedItem()
		if uid:
			self.LoadChart(uid)

	def GetSelectedItem(self):
		index = self.list.GetNextItem(-1,
								wx.LIST_NEXT_ALL,
								wx.LIST_STATE_SELECTED)
		return self.list.GetItemText(index) if index != -1 else None

def Standalone(filename = None):
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1, "Report Reader", size = (800, 600))
	p = ReportTab(frame)

	if filename:
		p.LoadReport(filename)

	frame.Center()
	frame.Show(True)
	app.MainLoop()

if __name__ == '__main__':
	import Test
	Test.TestPanel(ReportTab, lambda p:p.LoadReport('reports/tmp/q.db'))

