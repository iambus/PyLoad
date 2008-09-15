
import wx
import IconImages

import RecordPanel

import Record


class ColoredPanel(wx.Window):
	def __init__(self, parent, color):
		wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
		self.SetBackgroundColour(color)


class NoteBook(wx.Toolbook):
	def __init__(self, parent, id):
		wx.Toolbook.__init__(self, parent, id, style=wx.BK_TOP)


		self.AssignImageList(wx.ImageList(0,0))

		self.recordTab = RecordPanel.RecordPanel(self)
		self.AddPage(self.recordTab, 'Record', imageId=-1)
		self.recordTab.ResetSize()

		colourList = [ "Design", "Runtime", "Result", ]
		g = self.makeColorPanel()
		for colour in colourList:
			win = g.next()
			self.AddPage(win, colour, imageId=-1)


	def makeColorPanel(self):
		colourList = [ "Aquamarine", "Blue Violet", "Brown", ]
		for color in colourList:
			p = wx.Panel(self, -1)
			win = ColoredPanel(p, color)
			p.win = win
			def OnCPSize(evt, win=win):
				win.SetPosition((0,0))
				win.SetSize(evt.GetSize())
			p.Bind(wx.EVT_SIZE, OnCPSize)
			yield p


class MainFrame(wx.Frame):

	def __init__(self):
		wx.Frame.__init__(self, None, -1, "PyLoad", size=(800, 600))

		self.nb = NoteBook(self, -1)

		self.InitIcons()
		self.UseMenuBar()
		self.UseToolBar()

	def InitIcons(self):
		self.startIcon = IconImages.getStartBitmap()
		self.startIconOff = IconImages.getStartOffBitmap()

		self.stopIcon = IconImages.getStopBitmap()
		self.stopIconOff = IconImages.getStopOffBitmap()

		self.runIcon = IconImages.getRunBitmap()
		self.runIconOff = IconImages.getRunOffBitmap()

		self.terminateIcon = IconImages.getTerminateBitmap()
		self.terminateIconOff = IconImages.getTerminateOffBitmap()


	# {{{ Menu
	def menuData(self):
		return [
				("&File", (
					("&Save\tCtrl+S", "Save file", self.OnSave),
					("", "", ""),
					("E&xit", "Exit", self.OnExit),
					("", "", ""),
					)),
				("&Op", 
					(
					("Record\tF5", "Record", self.OnRecord, True, self.startIcon, self.stopIconOff),
					("Stop Recoding\tF6", "Record", self.OnStop, False, self.stopIcon, self.stopIconOff),
					("", "", ""),
					("Run\tF7", "Run", self.OnRun, True, self.runIcon, self.runIconOff),
					("Terminate\tF8", "Terminate", self.OnTerminate, False, self.terminateIcon, self.terminateIconOff),
					)),
				("&Help", (
					("&About", "", self.OnAll),
					)),
				]

	def UseMenuBarFrom(self, data):
		menuBar = wx.MenuBar()
		for eachMenuData in data:
			menuLabel = eachMenuData[0]
			menuItems = eachMenuData[1]
			menuBar.Append(self.CreateMenu(menuItems), menuLabel)
		self.SetMenuBar(menuBar)

	def CreateMenu(self, menuData):
		menu = wx.Menu()
		for eachItem in menuData:
			if len(eachItem) == 2:
				label = eachItem[0]
				subMenu = self.CreateMenu(eachItem[1])
				menu.AppendMenu(wx.NewId(), label, subMenu)
			else:
				self.CreateMenuItem(menu, *eachItem)
		return menu

	def CreateMenuItem(self, menu, label, status, handler, enabled = None, icon = None, icon2 = None):
		kind = wx.ITEM_NORMAL

		if not label:
			menu.AppendSeparator()
			return
		menuItem = wx.MenuItem(menu, wx.NewId(), label, status, kind)
		if icon:
			menuItem.SetBitmaps(icon, icon2)
		menu.AppendItem(menuItem)
		if enabled == False:
			menuItem.Enable(enabled)

		self.Bind(wx.EVT_MENU, handler, menuItem)

	def UseMenuBar(self):
		self.UseMenuBarFrom(self.menuData())
		#menuBar = wx.MenuBar()
		#menu = wx.Menu()
		#menuBar.Append(menu, 'File')
		#self.SetMenuBar(menuBar)
	# }}}

	def UseToolBar(self):
		toolbar = self.CreateToolBar()

		start = self.createTool(toolbar, "Record", self.startIcon, self.startIconOff)
		self.Bind(wx.EVT_MENU, self.OnRecord, start)

		stop = self.createTool(toolbar, "Stop Record", self.stopIcon, self.stopIconOff)
		self.Bind(wx.EVT_MENU, self.OnStop, stop)

		toolbar.AddSeparator()

		run = self.createTool(toolbar, "Run", self.runIcon, self.runIconOff)
		self.Bind(wx.EVT_MENU, self.OnRun, run)

		terminate = self.createTool(toolbar, "Terminate", self.terminateIcon, self.terminateIconOff)
		self.Bind(wx.EVT_MENU, self.OnTerminate, terminate)

		self.toolbar = toolbar
		self.toolStart = start
		self.toolStop = stop
		self.toolRun = run
		self.toolTerminate = terminate

		self.toolbar.EnableTool(self.toolStart.GetId(), 1)
		self.toolbar.EnableTool(self.toolStop.GetId(), 0)

		self.toolbar.EnableTool(self.toolRun.GetId(), 1)
		self.toolbar.EnableTool(self.toolTerminate.GetId(), 0)

		toolbar.Realize()

	def createTool(self, toolbar, label, icon1, icon2):
		return toolbar.AddLabelTool(wx.NewId(), label, icon1, icon2, shortHelp=label)

	def OnRecord(self, evt):
		self.toolbar.EnableTool(self.toolStart.GetId(), 0)
		self.toolbar.EnableTool(self.toolStop.GetId(), 1)
		menu = self.GetMenuBar().GetMenu(1)
		menu.FindItemByPosition(0).Enable(False)
		menu.FindItemByPosition(1).Enable(True)

		record = Record.Record()
		self.nb.recordTab.AppendNewRecord(record)


	def OnStop(self, evt):
		self.toolbar.EnableTool(self.toolStart.GetId(), 1)
		self.toolbar.EnableTool(self.toolStop.GetId(), 0)
		menu = self.GetMenuBar().GetMenu(1)
		menu.FindItemByPosition(0).Enable(True)
		menu.FindItemByPosition(1).Enable(False)


	def OnRun(self, evt):
		self.toolbar.EnableTool(self.toolRun.GetId(), 0)
		self.toolbar.EnableTool(self.toolTerminate.GetId(), 1)
		menu = self.GetMenuBar().GetMenu(1)
		menu.FindItemByPosition(3).Enable(False)
		menu.FindItemByPosition(4).Enable(True)
	
	def OnTerminate(self, evt):
		self.toolbar.EnableTool(self.toolRun.GetId(), 1)
		self.toolbar.EnableTool(self.toolTerminate.GetId(), 0)
		menu = self.GetMenuBar().GetMenu(1)
		menu.FindItemByPosition(3).Enable(True)
		menu.FindItemByPosition(4).Enable(False)

	def OnAll(self, event):
		print event

	def OnSave(self, event):
		print 'Save'

	def OnExit(self, event):
		self.Close()



def Main():
	app = wx.PySimpleApp()
	frame = MainFrame()
	frame.Center()
	frame.Show(True)
	app.MainLoop()

if __name__ == '__main__':
	Main()

# vim: foldmethod=marker:
