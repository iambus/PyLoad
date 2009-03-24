
import wx
import wx.lib.layoutf
from EditorPanel import EditorPanel


class FlyPanel(wx.Panel):
	def __init__(self, parent, **vars):
		wx.Panel.__init__(self, parent, -1)
		
		self.vars = vars
		
		self.editor = EditorPanel(self, -1)
		self.testButton = wx.Button(self, -1, "Run Script")

		if vars:
			welcome = '# You can use the following variables:\n'
			for k in sorted(vars.keys()):
				welcome += '# %s: %s\n' % (k, vars[k].__class__)
			welcome += '#\n'
			welcome += '# For example:\n'
			welcome += '# print %s\n' % sorted(vars.keys())[0]
			welcome += '#\n\n\n'

			self.editor.SetValue(welcome)
				
			# set caret position after the comments
			pos = len(welcome) - 1
#			self.editor.editor.SetCurrentPos(pos)
			self.editor.editor.SetSelection(pos, pos)

		# Layout
		self.SetAutoLayout(True)
		self.editor.SetConstraints(
			wx.lib.layoutf.Layoutf('t=t10#1;l=l10#1;b%b90#1;r=r10#1',(self,)))
		self.testButton.SetConstraints(
			wx.lib.layoutf.Layoutf('t_10#2;l=l10#1;h*;w*',(self,self.editor)))

		self.editor.saveButton.Hide()
		self.Bind(wx.EVT_BUTTON, self.OnPlay, self.testButton)


	def OnPlay(self, event):
		script = self.editor.GetValue()
		exec script in self.vars


class FlyFrame(wx.Frame):
	def __init__(self, parent, **vars):
		wx.Frame.__init__(self, parent, -1, "Fly")
		
		panel = FlyPanel(self, **vars)

		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

	def OnCloseWindow(self, event):
		self.Destroy()

def fly(parent, **vars):
	win = FlyFrame(parent, **vars)
	win.Show(True)

if __name__ == '__main__':

	class TestPanel(wx.Panel):
		def __init__(self, parent):
			wx.Panel.__init__(self, parent, -1)

			b = wx.Button(self, -1, "Create and Show a Frame", (50,50))
			self.Bind(wx.EVT_BUTTON, self.OnButton, b)

		def OnButton(self, evt):
			fly(self, m = 'hello')

	import Test
	Test.TestPanel(TestPanel)



