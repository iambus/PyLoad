
import wx
import Record
from Binding import *

def gg_attr_binding(name):
	return lambda data: AttrBinding(data, name)

def get_category(data):
	c = str(data.__class__)
	i = c.rfind('.') + 1
	return ConstBinding(c[i:])

LabelToBinding = {
		'ID': gg_attr_binding('uuid'),
		'Category': get_category,
		'URL': gg_attr_binding('url'),
		'Time': gg_attr_binding('timestr'),
}

ClassToLabels = {
	Record.Record : ('ID', 'Category', 'Time'),
	Record.Page   : ('ID', 'Category', 'Time'),
	Record.Hit    : ('ID', 'Category', 'Time', 'URL'),
#	Player.Script : ('Category',),
#	Controller.If : ('Category',),
#	Controller.Loop : ('Category',),
#	Special.Special : ('Category',),
#	PlayPolicy.Factory : ('Category',),
}

class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.fields = [
				]
		
		sizer = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
		sizer.AddGrowableCol(1)
		self.SetSizer(sizer)
		self.SetAutoLayout(True)

	def Load(self, data):
		c = data.__class__
		for label in ClassToLabels[c]:
			binding = LabelToBinding[label](data)
		self.LoadFields(map(lambda label: (label, LabelToBinding[label](data)), ClassToLabels[c]))

	def LoadFields(self, fields):
		n = len(self.fields)
		m = len(fields)
		if m < n:
			for i in range(m, n):
				self.fields[i][0].Hide()
				self.fields[i][1].Hide()
		elif n < m:
			for i in range(n, m):
				labelCtrl = wx.StaticText(self, -1, "", size = (64, -1), style=wx.ALIGN_RIGHT)
				inputCtrl = wx.TextCtrl(self, -1)
				inputCtrl.SetEditable(False)
				self.GetSizer().AddMany([
					#XXX: wx.ALIGN_CENTRE|wx.ALIGN_RIGHT should be wrong
					(labelCtrl, 0, wx.ALIGN_CENTRE|wx.ALIGN_RIGHT), (inputCtrl, 0, wx.EXPAND),
				])
				self.fields.append([labelCtrl, inputCtrl, None])
			assert len(fields) <= len(self.fields)
		assert len(fields) <= len(self.fields)
		for i in range(m):
			label, binding = fields[i]
			self.fields[i][0].SetLabel(label)
			self.fields[i][1].SetValue(binding.get())
			self.fields[i][2] = binding
			self.fields[i][0].Show()
			self.fields[i][1].Show()
		self.Layout()
	

if __name__ == '__main__':
	import Test
	from Binding import *
	def callback(p):
		class C:
			pass
		c = C()
		c.x = 'xxx'
		c.y = 'yyy'
		fields = (
			('a', AttrBinding(c, 'x')),
			('yyyy', AttrBinding(c, 'y')),
				)
		#p.LoadFields(fields)
		p.Load(Record.Hit('x'))
	Test.TestPanel(InfoPanel, callback)

