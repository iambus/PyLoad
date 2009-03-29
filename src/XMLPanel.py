
import wx
import wx.lib.layoutf
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from Tree import Tree

try:
	from lxml import etree
except ImportError:
	from xml.etree import ElementTree as etree
import sys

class XMLTree(Tree):
	def __init__(self, parent):
		Tree.__init__(self, parent)

		iconSize = self.iconSize
		icons = {
			'node': (wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize),
					 wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize)),
			'text': wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, iconSize),
			}
		self.SetIcons(icons)

	def SetXML(self, xml):
		try:
			self.xmltree = etree.fromstring(xml)
			self.AddTree(self.root, self.xmltree)
		except Exception, e:
			print e

	def GetLabel(self, element):
		return element.tag

	def GetChildren(self, element):
		return element.getchildren()

	def GetType(self, element):
		return 'node'

	def GetAttrPath(self, element):
		if not hasattr(element, 'attrTags') or not element.attrTags:
			return ''

		attrs = element.attrTags
		exp = ', '.join(["@%s='%s'" %(k, v) for k, v in attrs.items()])
		return '[%s]' % exp

	def GetXPath(self, node = None):
		if not node:
			node = self.GetSelected()
		if not node:
			return ''
		tokens = []
		while node != self.root:
			element = self.GetPyData(node)
			tokens.append(element.tag + self.GetAttrPath(element))
			node = self.GetItemParent(node)
		tokens.pop()
		tokens.reverse()
		xpath = '/'.join(tokens)
		return xpath




class AttributeList(wx.ListCtrl, CheckListCtrlMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
		CheckListCtrlMixin.__init__(self)
		self.InsertColumn(0, "Attribute")
		self.InsertColumn(1, "Value")
		self.SetColumnWidth(0, 100)
		self.SetColumnWidth(1, 200)


	def SetAttributes(self, attributes):
		self.DeleteAllItems()
		for attr in sorted(attributes.keys()):
			index = self.InsertStringItem(sys.maxint, attr)
			self.SetStringItem(index, 1, attributes[attr])
		self.attrs = {}
			
	def SetElement(self, element):
		self.element = element
		self.SetAttributes(element.attrib if element else {})

		if element and hasattr(element, 'attrTags'):
			for index in range(self.GetItemCount()):
				attr = self.GetItem(index, 0).GetText()
				value = self.GetItem(index, 1).GetText()
				if attr in element.attrTags:
					assert value == element.attrTags[attr]
					self.CheckItem(index)



	def OnCheckItem(self, index, flag):
		attr = self.GetItem(index, 0).GetText()
		value = self.GetItem(index, 1).GetText()
		if flag:
			self.attrs[attr] = value
		else:
			if attr in self.attrs:
				del self.attrs[attr]

		self.element.attrTags = self.attrs

		self.UpdateXPath()
				
	def UpdateXPath(self):
		pass




class XMLPanel(wx.Panel):
	def __init__(self, parent, xmlstr = ''):
		wx.Panel.__init__(self, parent, -1)
		
		self.xml = xmlstr

		self.splitter = wx.SplitterWindow(self, style=wx.BORDER_NONE)
		self.splitter2 = wx.SplitterWindow(self.splitter, style=wx.BORDER_NONE)


		leftPanel = wx.Panel(self.splitter, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

		self.tree = XMLTree(leftPanel)
		self.search = wx.SearchCtrl(leftPanel, -1, style=wx.TE_PROCESS_ENTER)
		self.search.ShowSearchButton(True)
		self.search.ShowCancelButton(True)
		menu = wx.Menu()
		self.textMenuItem = menu.AppendRadioItem(-1, "Tag/Text")
		self.xpathMenuItem = menu.AppendRadioItem(-1, "XPath")
		self.search.SetMenu(menu)


		self.attr = AttributeList(self.splitter2)
		self.text = wx.TextCtrl(self.splitter2, style=wx.TE_MULTILINE)
		self.text.SetEditable(False)

		self.splitter.SetMinimumPaneSize(120)
		self.splitter.SplitVertically(leftPanel, self.splitter2, 180)

		self.splitter2.SetMinimumPaneSize(160)
		self.splitter2.SplitHorizontally(self.attr, self.text, 180)


		xpathLabel = wx.StaticText(self, -1, "XPath")
		self.xpath = wx.TextCtrl(self)
		self.xpath.SetEditable(False)
		self.copy = wx.Button(self, -1, 'Copy To Clipboard')



		leftBox = wx.BoxSizer(wx.VERTICAL)
		leftBox.Add(self.tree, 1, wx.EXPAND)
		leftBox.Add(wx.StaticText(leftPanel, label = "Search in tree"), 0, wx.TOP|wx.LEFT, 5)
		leftBox.Add(self.search, 0, wx.EXPAND|wx.ALL, 5)
		leftPanel.SetSizer(leftBox)

		self.SetAutoLayout(True)
		self.splitter.SetConstraints(
			wx.lib.layoutf.Layoutf('t=t10#1;l=l10#1;b%b90#1;r=r10#1',(self,)))
		xpathLabel.SetConstraints(
			wx.lib.layoutf.Layoutf('t_10#2;l=l10#1;h*;w*',(self,self.splitter)))
		self.xpath.SetConstraints(
			wx.lib.layoutf.Layoutf('t_10#2;l>r10#3;h*;r=r150#1',(self,self.splitter, xpathLabel)))
		self.copy.SetConstraints(
			wx.lib.layoutf.Layoutf('t_10#2;l>r10#3;h*;r=r10#1',(self,self.splitter, self.xpath)))



		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)

#		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
		self.Bind(wx.EVT_TEXT, self.OnIncrSearch, self.search)        

		self.attr.UpdateXPath = self.UpdateXPath
		self.Bind(wx.EVT_BUTTON, self.CopyToClipboard, self.copy)

		if xmlstr.strip():
			self.InitXML()


	def InitXML(self, xmlstr = None):
		if xmlstr:
			self.xml = xmlstr
		self.tree.SetXML(self.xml)


	def OnSelChanged(self, event):
		# TODO: if unselected
		item = event.GetItem()
		if item and item != self.tree.root:
			item = self.tree.GetSelected()
			data = self.tree.GetPyData(item)
			self.attr.SetElement(data)
			self.text.SetValue(data.text)
			self.UpdateXPath(item)


	def Search(self):
		keyword = self.search.GetValue()
		if keyword:
			if self.textMenuItem.IsChecked():
				nodeFilter = lambda element: keyword in element.tag or keyword in element.text
			else:
				try:
					elements = self.tree.xmltree.findall(keyword)
					nodeFilter = lambda element: element in elements
				except SyntaxError, e:
					nodeFilter = lambda elements: False
					print e
					
			self.tree.FilterTree(nodeFilter)
		else:
			self.tree.RestoreTree()

	def OnSearch(self, event):
		self.Search()

	def OnIncrSearch(self, event):
		if self.xpathMenuItem.IsChecked():
			return
		self.Search()

	def OnCancel(self, event):
		self.tree.RestoreTree()

	def UpdateXPath(self, node = None):
		xpath = self.tree.GetXPath(node)
		self.xpath.SetValue(xpath)



	def CopyToClipboard(self, event = None):
		xpath = self.xpath.GetValue()
		data = wx.TextDataObject()
		data.SetText(xpath)
		wx.TheClipboard.Open()
		wx.TheClipboard.SetData(data)
		wx.TheClipboard.Close()

	def ResetSize(self):
		self.splitter.SetSashPosition(100)
		self.splitter2.SetSashPosition(100)



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
	import Test
	Test.TestPanel(XMLPanel, lambda p: p.InitXML(xml))

