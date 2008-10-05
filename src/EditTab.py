
import wx
from wx.lib.splitter import MultiSplitterWindow

from ControllersPanel import ControllersPanel
from SpecialsPanel import SpecialsPanel
from DetailsPanel import DetailsPanel
from RecordPanel import RecordPanel

class ColoredPanel(wx.Window):
	def __init__(self, parent, color = 'red'):
		wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
		self.SetBackgroundColour(color)



class EditTab(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.splitter = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
		self.leftsplitter = wx.SplitterWindow(self.splitter, style=wx.BORDER_NONE)

		p1 = ControllersPanel(self.leftsplitter)
		p2 = RecordPanel(self.leftsplitter, True)
		self.leftsplitter.SplitHorizontally(p1, p2, -300)

		p3 = SpecialsPanel(self.splitter)
		p4 = DetailsPanel(self.splitter)
		self.splitter.AppendWindow(self.leftsplitter, 180)
		self.splitter.AppendWindow(p3, 180)
		self.splitter.AppendWindow(p4, 150)

		self.controllersPanel = p1
		self.specialsPanel = p3
		self.detailsPanel = p4
		self.recordPanel = p2

		# layout
		import Layout
		Layout.SingleLayout(self, self.splitter)

		# bindings
		self.Bind(wx.EVT_BUTTON, self.OnPlay, self.detailsPanel.testButton)
		self.specialsPanel.onSelChangedCallback = self.detailsPanel.Load

	def OnPlay(self, event):
		tree = self.specialsPanel.tree
		player = tree.GetPyData(tree.GetSelection())
		player.play()

	def ResetSize(self):
		self.leftsplitter.SetSashPosition(180)

	def Unload(self):
		self.specialsPanel.Unload()
		self.recordPanel.Unload()
		self.detailsPanel.Unload()

	def Reload(self):
		self.specialsPanel.Reload()

if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1, "EditTab", size = (800, 600))
	p = EditTab(frame)

	import Project
	p.specialsPanel.project = Project.NoneProject()
	import Record
	p.recordPanel.AppendRecord(Record.Record())

	frame.Center()
	frame.Show(True)
	app.MainLoop()

