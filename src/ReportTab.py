
import wx
import LineChartPanel

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

		self.list.SetColumnWidth(0, 60)
		self.list.SetColumnWidth(1, 60)
		self.list.SetColumnWidth(2, 60)
		self.list.SetColumnWidth(3, 60)
		self.list.SetColumnWidth(4, 60)
		self.list.SetColumnWidth(5, 60)


		self.chartPanel = LineChartPanel.LineChart(self.splitter)
		self.chartPanel.xformat = LineChartPanel.XTimeFormatter
		self.chartPanel.yformat = LineChartPanel.YMSFormatter

		self.splitter.SplitHorizontally(self.list, self.chartPanel, 180)

		import Layout
		Layout.SingleLayout(self, self.splitter)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)

	def LoadReport(self, path):
		import sqlite3

		connection = sqlite3.connect(path)
		cursor = connection.cursor()

		cursor.execute('select id, label, avg, max, min, count from summary')
		self.summary = [row for row in cursor]
		self.LoadSummary(self.summary)

		cursor.execute('select hitid, timestamp, response_time from hits_v order by hitid, timestamp')
		self.data = [row for row in cursor]

		cursor.close()

	def LoadSummary(self, rows):
		self.list.DeleteAllItems()
		def tostr(v):
			if type(v) in [str, unicode]:
				return v
			elif type(v) in [float]:
				return '%.3f' % v
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

		if len(rows):
			self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)

	def LoadChart(self, uid):
		data = [hit[1:3] for hit in self.data if hit[0] == uid]
		self.chartPanel.SetData(data)

	# XXX: why I need this?
	def ResetSize(self):
		self.splitter.SetSashPosition(120)

	def OnItemSelected(self, event):
		uid = self.list.GetItemText(event.m_itemIndex)
		self.LoadChart(uid)

if __name__ == '__main__':
	import Test
	Test.TestPanel(ReportTab, lambda p:p.LoadReport('reports/last-report.db'))

