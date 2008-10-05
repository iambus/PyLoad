
import wx

import InfoPanel
import EditorPanel

from RecordPanel import RecordPanel
from DetailsPanel import DetailsPanel

import Record

import Logger
log = Logger.getLogger()

class ColoredPanel(wx.Window):
	def __init__(self, parent, color = 'red'):
		wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
		self.SetBackgroundColour(color)


##################################################
class RecordTab(wx.Panel):
	def __init__(self, parent):
		# Use the WANTS_CHARS style so the panel doesn't eat the Return key.
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

		#XXX: why can't I remove it?
		self.Bind(wx.EVT_SIZE, self.OnSize)

		self.splitter = wx.SplitterWindow(self, style=wx.BORDER_NONE)

		self.tree = RecordPanel(self.splitter)
		self.detailsPanel = DetailsPanel(self.splitter)

		self.splitter.SetMinimumPaneSize(20)
		self.splitter.SplitVertically(self.tree, self.detailsPanel, 180)

		sizer = wx.BoxSizer()
		sizer.Add(self.splitter, proportion=1, flag=wx.EXPAND)
		self.SetSizer(sizer) 

		# Event Binding
		self.Bind(wx.EVT_BUTTON, self.OnPlay, self.detailsPanel.testButton)
		self.tree.onSelChangedCallback = self.detailsPanel.Load

	########################################

	def ResetSize(self):
		self.splitter.SetSashPosition(170)

	########################################
	#XXX: why can't I remove it?
	def OnSize(self, event):
		event.Skip()

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
