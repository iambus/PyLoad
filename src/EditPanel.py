
import wx
from wx.lib.splitter import MultiSplitterWindow

from ControllersPanel import ControllersPanel
from SpecialsPanel import SpecialsPanel

class ColoredPanel(wx.Window):
	def __init__(self, parent, color = 'red'):
		wx.Window.__init__(self, parent, -1, style = wx.SIMPLE_BORDER)
		self.SetBackgroundColour(color)



class EditPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.splitter = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
		self.leftsplitter = wx.SplitterWindow(self.splitter, style=wx.BORDER_NONE)

		p1 = ControllersPanel(self.leftsplitter)
		p2 = ColoredPanel(self.leftsplitter, 'pink')
		self.leftsplitter.SplitHorizontally(p1, p2, -300)

		p3 = SpecialsPanel(self.splitter)
		p4 = ColoredPanel(self.splitter, 'gray')
		self.splitter.AppendWindow(self.leftsplitter, 180)
		self.splitter.AppendWindow(p3, 180)
		self.splitter.AppendWindow(p4, 150)

		import Layout
		Layout.SingleLayout(self, self.splitter)

	def ResetSize(self):
		self.leftsplitter.SetSashPosition(180)

if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1, "EditPanel", size = (800, 600))
	p = EditPanel(frame)

	frame.Center()
	frame.Show(True)
	app.MainLoop()

