
import wx

class Tabs(wx.Notebook):
	def __init__(self, parent):
		wx.Notebook.__init__(self, parent, -1)

	def GetTabNames(self, data):
		raise NotImplementedError()

	def InitTab(self, tabName, tab, data):
		raise NotImplementedError()

	def CreateTab(self, tabName):
		raise NotImplementedError()

	def GetTabType(self, tabName):
		return tabName

	def GiveSharedTabs(self, newTabNames):
		'Avoid re-creating the same tabs'
		currentTabNames = []
		for i in range(self.GetPageCount()):
			currentTabNames.append(self.GetPageText(i))
		minlen = min( len(currentTabNames), len(newTabNames) )
		n = 0
		while n < minlen and self.GetTabType(currentTabNames[n]) == self.GetTabType(newTabNames[n]):
			n += 1
		if n == 0:
			self.DeleteAllPages()
			return 0
		else:
			for i in range(n, len(currentTabNames)):
				self.DeletePage(n)
			return n

	def Load(self, data, update = False):
		if data == None:
			# possible on Linux
			# TODO: auto-select next node on Linux when a node is deleted (of course not here)
			self.Unload()
			return

		if update:
			self.UpdateInfo(data)
		else:
			self.LoadData(data)

	def ReLoad(self, data):
		'Always create new tabs'
		self.DeleteAllPages()
		tabNames = self.GetTabNames(data)
		for tabName in tabNames:
			tab = self.CreateTab(tabName)
			self.AddPage(tab, tabName)
			self.InitTab(tabName, tab, data)

	def Unload(self):
		self.DeleteAllPages()

	def LoadData(self, data):
		self.Freeze()
		try:
			'Avoid re-creating the same tabs'
			tabNames = self.GetTabNames(data)

			n = self.GiveSharedTabs(tabNames)

			for i in range(n):
				tab = self.GetPage(i)
				tabName = tabNames[i]
				self.SetPageText(i, tabName)
				self.InitTab(tabName, tab, data)

			for i in range(n, len(tabNames)):
				tabName = tabNames[i]
				tab = self.CreateTab(tabName)
				self.AddPage(tab, tabName)
				self.InitTab(tabName, tab, data)
		finally:
			self.Thaw()

	def UpdateInfo(self, data):
		tabName = self.GetPageText(0)
		assert tabName == 'Info'
		tab = self.GetPage(0)
		tab.Load(data)

if __name__ == '__main__':
	class InfoTab(wx.TextCtrl):
		def __init__(self, parent):
			wx.TextCtrl.__init__(self, parent, style=wx.TE_MULTILINE)
	class MyTabs(Tabs):
		def GetTabNames(self, data):
			return ('Info', 'MoreInfo')
		def InitTab(self, tabName, tab, data):
			tab.SetValue(data)
		def CreateTab(self, tabName):
			return InfoTab(self)

	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1, "TestPanel", size = (800, 600))
	tabs = MyTabs(frame)
	tabs.Load('haha')

	frame.Center()
	frame.Show(True)
	app.MainLoop()

