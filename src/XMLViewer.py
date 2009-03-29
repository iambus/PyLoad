

import wx
from XMLPanel import XMLPanel
from editor.CodeCtrl import CodeCtrl


class XMLViewer(wx.Panel):
	def __init__(self, parent, xmlstr = ''):
		wx.Panel.__init__(self, parent, -1)

		self.nb = wx.Notebook(self, -1, style = wx.BK_BOTTOM)
		self.viewPanel = XMLPanel(self.nb, xmlstr)
		self.sourcePanel = CodeCtrl(self.nb, -1,
									style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
		import editor.syntax.xml
		self.sourcePanel.SetSyntax(editor.syntax.xml)
		self.sourcePanel.SetValue(xmlstr)

		self.nb.AddPage(self.viewPanel, "View")
		self.nb.AddPage(self.sourcePanel, "Source")


		import Layout
		Layout.SingleLayout(self, self.nb)


		self.viewPanel.ResetSize()


class XMLFrame(wx.Frame):
	def __init__(self, parent, xmlstr = ''):
		wx.Frame.__init__(self, parent, -1, "XLM Viewer", size = (540, 420))
		
		panel = XMLViewer(self, xmlstr)


		# XXX: do we need this?
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

		panel.viewPanel.ResetSize()

	def OnCloseWindow(self, event):
		self.Destroy()



def ShowXML(parent, xmlstr = ''):
	win = XMLFrame(parent, xmlstr)
	win.Show(True)


def FindAndShowXML(parent, xmlstr):
	index = xmlstr.find('<')
	if index >= 0:
		xmlstr = xmlstr[index:]
	else:
		index = ''
	ShowXML(parent, xmlstr)

if __name__ == '__main__':
	xml = '''
<list>
	<item class='good'>Dream</item>
	<item class='bad'>city</item>
	<others class = 'any'>
		<item>nothing</item>
	</others>
</list>
'''
	app = wx.PySimpleApp()
	ShowXML(None, xml)
	app.MainLoop()
#	import Test
#	Test.TestPanel(XMLViewer)

