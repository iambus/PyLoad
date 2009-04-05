
import wx
import wx.aui

import InfoPanel
import EditorPanel

from RecordPanel import RecordPanel
from DetailsPanel import DetailsPanel

import Record

import Logger
log = Logger.getLogger()


##################################################
class RecordTab(wx.Panel):
	def __init__(self, parent):
		# Use the WANTS_CHARS style so the panel doesn't eat the Return key.
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

		self.tree = RecordPanel(self)
		self.detailsPanel = DetailsPanel(self)

		# Event Binding
		self.Bind(wx.EVT_BUTTON, self.OnPlay, self.detailsPanel.testButton)
		self.tree.onSelChangedCallback = self.detailsPanel.Load


		self.mgr = wx.aui.AuiManager()
		self.mgr.SetManagedWindow(self)

		self.mgr.AddPane(self.tree,
						 wx.aui.AuiPaneInfo().
						 Left().
						 BestSize((240,-1)).MinSize((160,-1)).FloatingSize((160, -1)).
						 Caption("Records").
						 MaximizeButton(True).
						 MinimizeButton(True).
						 PinButton(True).
						 CloseButton(False))

		self.mgr.AddPane(self.detailsPanel,
						 wx.aui.AuiPaneInfo().
						 CenterPane().
						 MaximizeButton(True))

		self.mgr.Update()


	########################################

	def OnExit(self):
		self.tree.DeleteAllItems()

	def OnPlay(self, event):
		self.Play()

	########################################

	def Unload(self):
		self.tree.Unload()
		self.detailsPanel.Unload()

	def Reload(self):
		self.tree.Reload()

	def Play(self):
		self.tree.tree.SelectedData().play()
	
	########################################


##################################################



if __name__ == '__main__':
	app = wx.PySimpleApp()
	#app.RedirectStdio()

	#frame = RecordTab(None)
	frame = wx.Frame(None, -1, "RecoradPanel", size = (800, 600))
	rt = RecordTab(frame)
	import Record
	import Project
	rt.tree.project = Project.NoneProject()
	rt.tree.AppendNewRecord(Record.Record())
	rt.tree.AppendNewHit(Record.Hit('/'))
	rt.tree.AppendNewHit(Record.Hit('/'))
	rt.tree.AppendNewHit(Record.Hit('/m3oui'))
	rt.tree.AppendNewRecord(Record.Record())
	rt.tree.AppendNewHit(Record.Hit('/'))


	frame.Center()
	frame.Show(True)
	app.MainLoop()


# vim: foldmethod=marker
