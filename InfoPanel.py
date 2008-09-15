
import wx

class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		
		categoryLabel = wx.StaticText(self, -1, "Category")
		categoryField = wx.TextCtrl(self, -1)
		timeLabel = wx.StaticText(self, -1, "Time")
		timeField = wx.TextCtrl(self, -1)

		self.categoryField = categoryField
		self.timeField = timeField

		sizer = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
		sizer.AddGrowableCol(1)
		sizer.AddMany([
			#XXX: wx.ALIGN_CENTRE|wx.ALIGN_RIGHT should be wrong
			(categoryLabel, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT), (categoryField, 0, wx.EXPAND),
			(    timeLabel, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT), (    timeField, 0, wx.EXPAND),
			])
		self.SetSizer(sizer)
		self.SetAutoLayout(True)


	def Load(self, data):
		self.categoryField.SetValue(self.GetCategory(data))
		self.timeField.SetValue(data.timestr)
	
	def GetCategory(self, data):
		c = str(data.__class__)
		i = c.rfind('.') + 1
		return c[i:]

