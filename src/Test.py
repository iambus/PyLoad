
import wx

def TestPanel(Panel, callback = None):
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1, "EditPanel", size = (800, 600))
	p = Panel(frame)

	if callback:
		callback(p)

	frame.Center()
	frame.Show(True)
	app.MainLoop()

