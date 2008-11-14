
import sys
import wx
import IconImages

from RecordTab import RecordTab
from EditTab import EditTab
from PlayTab import PlayTab
from ReportTab import ReportTab

import Record
from Project import Project
from Report import Report
import ReportManager

from proxy import Proxy

# For unimplemented panel...
class ColoredPanel(wx.Window):
	def __init__(self, parent, color):
		wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
		self.SetBackgroundColour(color)

# {{{ NoteBook
class NoteBook(wx.Toolbook):
	def __init__(self, parent, id, project = None, reporter = None):
		wx.Toolbook.__init__(self, parent, id, style=wx.BK_TOP)

		images = wx.ImageList(32, 32)
		if sys.platform == 'linux2':
			# Must set icons for Linux
			images.Add(IconImages.getRecordTabBitmap())
			images.Add(IconImages.getEditTabBitmap())
			images.Add(IconImages.getPlayTabBitmap())
			images.Add(IconImages.getReportTabBitmap())
		self.AssignImageList(images)

		self.recordTab = RecordTab(self)
		self.AddPage(self.recordTab, 'Record', imageId=0)
		self.recordTab.ResetSize()

		self.editTab = EditTab(self)
		self.AddPage(self.editTab, 'Edit', imageId=1)
		self.editTab.ResetSize()

		self.editTab.recordPanel.SetMirrorOf(self.recordTab.tree)
		self.recordTab.tree.AddObserver(self.editTab.specialsPanel.UpdateAll)

		self.playTab = PlayTab(self, project, reporter)
		self.AddPage(self.playTab, 'Play', imageId=2)
		self.playTab.ResetSize()

		self.editTab.specialsPanel.onNewSpecialCallback = self.playTab.policyPanel.UpdateSpecials

		self.reportTab = ReportTab(self)
		self.AddPage(self.reportTab, 'Report', imageId=3)
		self.reportTab.ResetSize()


# }}}

import wx.lib.newevent
(PlayEvent, EVT_PLAY_STOPPED) = wx.lib.newevent.NewEvent()

class MainFrame(wx.Frame):

	# {{{ init
	def __init__(self):
		wx.Frame.__init__(self, None, -1, "PyLoad", size=(800, 600))

		self.InitProject()
		self.project = Project()
		self.reportPath = 'reports/last-report.db'
		self.report = Report(self.reportPath)
		self.path = None

		self.nb = NoteBook(self, -1, self.project, self.report)

		self.InitIcons()
		self.UseMenuBar()
		self.UseToolBar()

		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(EVT_PLAY_STOPPED, self.OnPlayStopped)

		#TODO: put in tabs' constructors
		self.nb.recordTab.tree.project = self.project
		self.nb.editTab.specialsPanel.project = self.project
		self.proxy = None

	def InitProject(self):
		import os, os.path
		if not os.path.exists('reports'):
			os.mkdir('reports')

	def InitIcons(self):
		if sys.platform == 'linux2':
			iconSize = (24, 24)
		else:
			iconSize = (16, 16)
		self.newIcon = wx.ArtProvider_GetBitmap(wx.ART_NEW, wx.ART_OTHER, iconSize)
		self.newIconOff = wx.ArtProvider_GetBitmap(wx.ART_ERROR, wx.ART_OTHER, iconSize) #TODO: add correct icon
		self.openIcon = wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, iconSize)
		self.openIconOff = wx.ArtProvider_GetBitmap(wx.ART_ERROR, wx.ART_OTHER, iconSize) #TODO: add correct icon
		self.saveIcon = wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, iconSize)
		self.saveIconOff = wx.ArtProvider_GetBitmap(wx.ART_ERROR, wx.ART_OTHER, iconSize) #TODO: add correct icon
		self.saveAsIcon = wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_OTHER, iconSize)
		self.saveAsIconOff = wx.ArtProvider_GetBitmap(wx.ART_ERROR, wx.ART_OTHER, iconSize) #TODO: add correct icon

		self.startIcon = IconImages.getStartBitmap()
		self.startIconOff = IconImages.getStartOffBitmap()

		self.stopIcon = IconImages.getStopBitmap()
		self.stopIconOff = IconImages.getStopOffBitmap()

		self.playIcon = IconImages.getRunBitmap()
		self.playIconOff = IconImages.getRunOffBitmap()

		self.terminateIcon = IconImages.getTerminateBitmap()
		self.terminateIconOff = IconImages.getTerminateOffBitmap()
	# }}}

	# {{{ Menu
	def menuData(self):
		return [
				("&File", (
					("&New\tCtrl+N", "New Project", self.OnNew),
					("&Open\tCtrl+O", "Open Project", self.OnOpen),
					("&Report\tCtrl+R", "Open Report", self.OnOpenReport),
					("&Save\tCtrl+S", "Save Project", self.OnSave),
					("Save &As", "Save Project As...", self.OnSaveAs),
					("", "", ""),
					("E&xit", "Exit", self.OnExit),
					)),
				("&Operation", 
					(
					("Record\tF5", "Record", self.OnRecord, True, self.startIcon, self.stopIconOff),
					("Stop Recoding\tF6", "Stop Recording", self.OnStop, False, self.stopIcon, self.stopIconOff),
					("", "", ""),
					("Play\tF7", "Play", self.OnPlay, True, self.playIcon, self.playIconOff),
					("Terminate\tF8", "Stop Playing", self.OnTerminate, False, self.terminateIcon, self.terminateIconOff),
					)),
				("&View", 
					(
					("Record\tCtrl+1", "Record", self.OnRecordViewSelected),
					("Edit\tCtrl+2", "Edit", self.OnEditViewSelected),
					("Play\tCtrl+3", "Play", self.OnPlayViewSelected),
					("Report\tCtrl+4", "Report", self.OnReportViewSelected),
					)),
#				("&Util", 
#					(
#					("Reload Module\tCtrl+l", "Reload Module", self.OnReloadModule),
#					)),
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

	# {{{ ToolBar
	def UseToolBar(self):
		toolbar = self.CreateToolBar()

		new = toolbar.AddSimpleTool(wx.NewId(), self.newIcon, "New")
		self.Bind(wx.EVT_MENU, self.OnNew, new)

		open = toolbar.AddSimpleTool(wx.NewId(), self.openIcon, "Open")
		self.Bind(wx.EVT_MENU, self.OnOpen, open)

		save = toolbar.AddSimpleTool(wx.NewId(), self.saveIcon, "Save")
		self.Bind(wx.EVT_MENU, self.OnSave, save)

		saveAs = toolbar.AddSimpleTool(wx.NewId(), self.saveAsIcon, "Save As")
		self.Bind(wx.EVT_MENU, self.OnSaveAs, saveAs)

		toolbar.AddSeparator()

		start = self.createTool(toolbar, "Record", self.startIcon, self.startIconOff)
		self.Bind(wx.EVT_MENU, self.OnRecord, start)

		stop = self.createTool(toolbar, "Stop Record", self.stopIcon, self.stopIconOff)
		self.Bind(wx.EVT_MENU, self.OnStop, stop)

		toolbar.AddSeparator()

		play = self.createTool(toolbar, "Play", self.playIcon, self.playIconOff)
		self.Bind(wx.EVT_MENU, self.OnPlay, play)

		terminate = self.createTool(toolbar, "Terminate", self.terminateIcon, self.terminateIconOff)
		self.Bind(wx.EVT_MENU, self.OnTerminate, terminate)

		self.toolbar = toolbar
		self.toolStart = start
		self.toolStop = stop
		self.toolPlay = play
		self.toolTerminate = terminate

		self.toolbar.EnableTool(self.toolStart.GetId(), 1)
		self.toolbar.EnableTool(self.toolStop.GetId(), 0)

		self.toolbar.EnableTool(self.toolPlay.GetId(), 1)
		self.toolbar.EnableTool(self.toolTerminate.GetId(), 0)

		toolbar.Realize()

	def createTool(self, toolbar, label, icon1, icon2):
		return toolbar.AddLabelTool(wx.NewId(), label, icon1, icon2, shortHelp=label)
	# }}}

	# {{{ Event handlers
	def OnRecord(self, event):
		self.toolbar.EnableTool(self.toolStart.GetId(), 0)
		self.toolbar.EnableTool(self.toolStop.GetId(), 1)
		menu = self.GetMenuBar().GetMenu(1)
		menu.FindItemByPosition(0).Enable(False)
		menu.FindItemByPosition(1).Enable(True)

		record = Record.Record()
		self.nb.recordTab.tree.AppendNewRecord(record)

		if self.proxy == None:
			self.proxy = Proxy.thread_start()

		Proxy.begin_catch(
				callback = self.nb.recordTab.tree.AppendNewHit,
				filter = Proxy.WebFilter
				)

	def OnStop(self, event):
		self.toolbar.EnableTool(self.toolStart.GetId(), 1)
		self.toolbar.EnableTool(self.toolStop.GetId(), 0)
		menu = self.GetMenuBar().GetMenu(1)
		menu.FindItemByPosition(0).Enable(True)
		menu.FindItemByPosition(1).Enable(False)

		Proxy.end_catch()


	def OnPlay(self, event):

		if self.nb.playTab.policyPanel.specialField.GetData() == None:
			# nothing to play
			return

		self.toolbar.EnableTool(self.toolPlay.GetId(), 0)
		self.toolbar.EnableTool(self.toolTerminate.GetId(), 1)
		menu = self.GetMenuBar().GetMenu(1)
		menu.FindItemByPosition(3).Enable(False)
		menu.FindItemByPosition(4).Enable(True)

		self.Play()

	def OnTerminate(self, event):
		Record.CANCELLED = True

	def OnPlayStopped(self, event):
		Record.CANCELLED = False
		self.toolbar.EnableTool(self.toolPlay.GetId(), 1)
		self.toolbar.EnableTool(self.toolTerminate.GetId(), 0)
		menu = self.GetMenuBar().GetMenu(1)
		menu.FindItemByPosition(3).Enable(True)
		menu.FindItemByPosition(4).Enable(False)

		self.SaveReport()
		self.nb.reportTab.LoadReport(self.reportPath)
		self.nb.SetSelection(3) # You may not like it.

	def OnRecordViewSelected(self, event):
		self.nb.SetSelection(0)

	def OnEditViewSelected(self, event):
		self.nb.SetSelection(1)

	def OnPlayViewSelected(self, event):
		self.nb.SetSelection(2)

	def OnReportViewSelected(self, event):
		self.nb.SetSelection(3)

	def OnReloadModule(self, event):
		dialog = wx.TextEntryDialog(
				self, 'Please enter the module name to reload',
				'Reload Module')
		moduleName = dialog.GetValue() if dialog.ShowModal() == wx.ID_OK else None
		dialog.Destroy()

		if moduleName == None or moduleName == '':
			return

		m = __import__(moduleName)
		reload(m)

	def OnAll(self, event):
		print event

	def OnNew(self, event):
		raise NotImplementedError('New')

	def OnOpen(self, event):
		path = None
		wildcard = "pickle (*.pkl)|*.pkl|"     \
				   "All files (*.*)|*.*"
		dialog = wx.FileDialog(
				self, message="Open Project", defaultDir="",
				defaultFile="", wildcard=wildcard, style=wx.OPEN
				)
		dialog.SetFilterIndex(0)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
		dialog.Destroy()
		if path:
			self.LoadProjectFrom(path)

	def OnOpenReport(self, event):
		path = None
		wildcard = "sqlite3 (*.db)|*.db|"     \
				   "All files (*.*)|*.*"
		dialog = wx.FileDialog(
				self, message="Open Report", defaultDir="",
				defaultFile="", wildcard=wildcard, style=wx.OPEN
				)
		dialog.SetFilterIndex(0)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
		dialog.Destroy()
		if path:
			self.nb.reportTab.LoadReport(path)
			self.nb.SetSelection(3)

	def OnSave(self, event):
		self.nb.playTab.Save()
		self.SaveProjectTo(self.path)

	def OnSaveAs(self, event):
		self.SaveProjectTo(None)


	def OnExit(self, event):
		self.Close()

	def OnClose(self, event):
		# TODO: Stopping playing before exiting
		Record.CANCELLED = True # not enough

		if self.proxy:
			Proxy.stop()
			self.proxy.join()
			self.proxy = None

		import proxy.Agent as poster
		poster.kill_if()
		
		self.Destroy()
	
	# }}}

	def UnloadAll(self):
		self.nb.recordTab.Unload()
		self.nb.editTab.Unload()
		self.nb.playTab.Unload()

	def ReloadAll(self):
		self.nb.recordTab.Reload()
		self.nb.editTab.Reload()
		self.nb.playTab.Reload()

	def LoadProjectFrom(self, path):
		assert path
		self.path = path
		self.UnloadAll()
		self.project.load_as_global(path)
		self.ReloadAll()

		self.SetTitle(path + ' - PyLoad')

	def SaveProjectTo(self, path):
		if not path:
			wildcard = "pickle (*.pkl)|*.pkl|"     \
					   "All files (*.*)|*.*"
			dialog = wx.FileDialog(
					self, message="Save file as ...", defaultDir="",
					defaultFile="", wildcard=wildcard, style=wx.SAVE
					)
			dialog.SetFilterIndex(0)
			if dialog.ShowModal() == wx.ID_OK:
				path = dialog.GetPath()
			dialog.Destroy()
			if not path:
				return
		self.path = path
		self.project.save(path)

		self.SetTitle(path + ' - PyLoad')

	def Play(self):
		import datetime
		startTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		policyPanel = self.nb.playTab.policyPanel
		userCount = policyPanel.userField.GetValue()
		iterationCount = policyPanel.iterationField.GetValue()
		special = policyPanel.specialField.GetData()
		specialLabel = special.label if special else '<empty>'
		summary = 'Start Time: %s\nUser Count: %s\nIteration Count: %s\nSpecial: %s' % (startTime, userCount, iterationCount, specialLabel)
		ReportManager.start_report(self.report, self.project, summary=summary)

		func = self.PlayInCurrentThread
		import threading
		class ProxyThread(threading.Thread):
			def __init__(self, name='ListenThread'):
				threading.Thread.__init__(self, name=name)
			def run(self):
				func()
		thread = ProxyThread() 
		thread.start()
	
	def PlayInCurrentThread(self):
		self.nb.playTab.Play()
		wx.PostEvent(self, PlayEvent())

	def SaveReport(self):
		self.report.finish()
		import datetime
		filename = 'reports/%s.db' % datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
		import shutil
		shutil.copyfile(self.report.path, filename)

def Main():
	import proxy.Agent as poster
	poster.fork_if()
		
	sys.path.append('runtime')
	sys.path.append('plugin')
	app = wx.PySimpleApp()
	frame = MainFrame()
	frame.Center()
	frame.Show(True)
	app.MainLoop()

if __name__ == '__main__':
	Main()

# vim: foldmethod=marker:
