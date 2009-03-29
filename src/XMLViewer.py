

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

	def SetXML(self, xmlstr):
		self.viewPanel.SetXML(xmlstr)
		self.sourcePanel.SetValue(xmlstr)

class SimpleFrame(wx.Frame):
	def __init__(self, parent, xmlstr = ''):
		wx.Frame.__init__(self, parent, -1, "XLM Viewer", size = (540, 420))
		
		panel = XMLViewer(self, xmlstr)

		# XXX: do we need this?
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

		panel.viewPanel.ResetSize()

	def OnCloseWindow(self, event):
		self.Destroy()


def ShowXML(parent, xmlstr = ''):
	win = SimpleFrame(parent, xmlstr)
	win.Show(True)

def FindAndShowXML(parent, xmlstr):
	index = xmlstr.find('<')
	if index >= 0:
		xmlstr = xmlstr[index:]
	else:
		index = ''
	ShowXML(parent, xmlstr)


class AppFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, -1, "XLM Viewer", size = (540, 420))

		menuBar = wx.MenuBar()
		menu = wx.Menu()
		menuBar.Append(menu, 'File')
		menuItem = menu.Append(wx.NewId(), 'Open')
		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnOpenFile, menuItem)
		
		self.viewer = XMLViewer(self)
		self.viewer.viewPanel.ResetSize()

	def OnOpenFile(self, event):
		import Dialog
		path = Dialog.OpenFile(self, 'XML', 'xml', 'Open XML File')
		if path:
			fp = open(path)
			xml = fp.read()
			fp.close()
			self.viewer.SetXML(xml)

def main():
	app = wx.PySimpleApp()
	win = AppFrame()
	win.Center()
	win.Show(True)
	app.MainLoop()

def test():
	xml = '''
<list>
	<item class='good'>Dream</item>
	<item class='bad'>city</item>
	<others class = 'any'>
		<item>nothing</item>
		<item/>
	</others>
</list>
'''
	app = wx.PySimpleApp()
	ShowXML(None, xml)
	app.MainLoop()
#	import Test
#	Test.TestPanel(XMLViewer)


if __name__ == '__main__':
	main()

