
import wx
import wx.aui
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


		p1 = ControllersPanel(self)
		p2 = RecordPanel(self, isMirror = True)
		p3 = SpecialsPanel(self)
		p4 = DetailsPanel(self)


		self.mgr = wx.aui.AuiManager()
		self.mgr.SetManagedWindow(self)


		self.mgr.AddPane(p1,
						 wx.aui.AuiPaneInfo().
						 Top().Left().Layer(1).
						 BestSize((240,-1)).MinSize((160,-1)).FloatingSize((160, -1)).
						 Caption("Controllers").
						 MaximizeButton(True).
						 PinButton(True).
						 CloseButton(False))

		self.mgr.AddPane(p2,
						 wx.aui.AuiPaneInfo().
						 Bottom().Left().Layer(1).
						 BestSize((240,-1)).MinSize((160,-1)).FloatingSize((160, -1)).
						 Caption("Records").
						 MaximizeButton(True).
						 PinButton(True).
						 CloseButton(False))

		self.mgr.AddPane(p3,
						 wx.aui.AuiPaneInfo().
						 Left().
						 BestSize((240,-1)).MinSize((160,-1)).FloatingSize((160, -1)).
						 Caption("Specials").
						 MaximizeButton(True).
						 PinButton(True).
						 CloseButton(False))

		self.mgr.AddPane(p4,
						  wx.aui.AuiPaneInfo().
						  CenterPane())


		self.mgr.Update()


		self.controllersPanel = p1
		self.specialsPanel = p3
		self.detailsPanel = p4
		self.recordPanel = p2

		# bindings
		self.Bind(wx.EVT_BUTTON, self.OnPlay, self.detailsPanel.testButton)
		self.specialsPanel.onSelChangedCallback = self.detailsPanel.Load

	def OnPlay(self, event):
		tree = self.specialsPanel.tree
		player = tree.GetPyData(tree.GetSelected())
		player.play()

	def Unload(self):
		self.specialsPanel.Unload()
		self.recordPanel.Unload()
		self.detailsPanel.Unload()

	def Reload(self):
		self.specialsPanel.Reload()
		self.controllersPanel.Reload()

if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1, "EditTab", size = (800, 600))
	p = EditTab(frame)

	import Project
	project = Project.NoneProject()
	import Record
	project.records.append(Record.Record())

	p.specialsPanel.project = project
	p.recordPanel.project = project

	frame.Center()
	frame.Show(True)
	app.MainLoop()

