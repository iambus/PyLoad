
import wx

import InfoPanel
import EditorPanel

from RecordTree import RecordTree
from DetailsPanel import DetailsPanel

import Record

import Logger
log = Logger.getLogger()

class ColoredPanel(wx.Window):
	def __init__(self, parent, color = 'red'):
		wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
		self.SetBackgroundColour(color)


##################################################
# {{{ Record Panel
class RecordPanel(wx.Panel):
	def __init__(self, parent):
		# Use the WANTS_CHARS style so the panel doesn't eat the Return key.
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

		self.Bind(wx.EVT_SIZE, self.OnSize)

		self.splitter = wx.SplitterWindow(self, style=wx.BORDER_NONE)

		self.tree = RecordTree(self.splitter)
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
	def OnSize(self, event):
		event.Skip()

	def OnExit(self):
		self.tree.DeleteAllItems()

	def OnPlay(self, event):
		self.Play()

	########################################

	def Play(self):
		self.tree.tree.SelectedData().play()
	
	########################################

# }}}

##################################################



if __name__ == '__main__':
	app = wx.PySimpleApp()
	#app.RedirectStdio()

	#frame = RecordPanel(None)
	frame = wx.Frame(None, -1, "RecoradPanel", size = (800, 600))
	rp = RecordPanel(frame)
	import Record
	rp.tree.AppendRecord(Record.Record())
	rp.tree.PostHit(Record.Hit('/'))
	rp.tree.PostHit(Record.Hit('/'))
	rp.tree.PostHit(Record.Hit('/m3oui'))


	frame.Center()
	frame.Show(True)
	app.MainLoop()


# vim: foldmethod=marker
