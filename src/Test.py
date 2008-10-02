
import wx

def TestPanel(Panel):
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1, "EditPanel", size = (800, 600))
	p = Panel(frame)

	frame.Center()
	frame.Show(True)
	app.MainLoop()

