
import wx

def SingleLayout(parent, component):
	sizer = wx.BoxSizer()
	sizer.Add(component, proportion=1, flag=wx.EXPAND)
	parent.SetSizer(sizer) 

