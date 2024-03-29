
import wx
import wx.lib.layoutf
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from control.Tree import Tree
import IconImages

try:
	from lxml import etree
except ImportError:
	from xml.etree import ElementTree as etree
import sys

class TreeNode:
	def __init__(self, element, children):
		self.element = element
		self.children = children
		self.attrs = {}

class XMLTree(Tree):
	def __init__(self, parent):
		Tree.__init__(self, parent)

		iconSize = self.iconSize
		icons = {
			'element': IconImages.getXMLElementBitmap(),
			}
		self.SetIcons(icons)


	def ElementToTreeNode(self, element):
		children = element.getchildren()
		return TreeNode(element, map(self.ElementToTreeNode, children))

	def SetXML(self, xml):
		try:
			self.eroot = etree.fromstring(xml)
			self.DeleteChildren(self.root)
			self.AddTree(self.root, self.ElementToTreeNode(self.eroot))
		except Exception, e:
			print e
			raise

	def GetLabel(self, node):
		return node.element.tag

	def GetChildren(self, node):
		return node.children

	def GetType(self, node):
		return 'element'

	def GetAttrPath(self, node):
		if not node.attrs:
			return ''

		attrs = node.attrs
		exp = ''.join(["[@%s='%s']" %(k, v) for k, v in attrs.items()])
		return exp

	def GetXPath(self, node = None):
		if not node:
			node = self.GetSelected()
		if not node:
			return ''
		tokens = []
		while node != self.root:
			n = self.GetPyData(node)
			tokens.append(n.element.tag + self.GetAttrPath(n))
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


	def SetElement(self, node):
		self.node = None
		self.DeleteAllItems()
		self.attrs = {}
		if node:
			attrs = node.element.attrib
			for attr in sorted(attrs.keys()):
				value = attrs[attr]
				index = self.InsertStringItem(sys.maxint, attr)
				self.SetStringItem(index, 1, value)
				if attr in node.attrs:
					assert value == node.attrs[attr]
					self.CheckItem(index)
					self.attrs[attr] = value
		self.node = node

	def OnCheckItem(self, index, flag):
		if not self.node:
			return

		attr = self.GetItem(index, 0).GetText()
		value = self.GetItem(index, 1).GetText()
		if flag:
			self.attrs[attr] = value
		else:
			if attr in self.attrs:
				del self.attrs[attr]

		self.node.attrs = self.attrs

		self.UpdateXPath()
				
	def UpdateXPath(self):
		pass




class XMLPanel(wx.Panel):
	def __init__(self, parent, xmlstr = ''):
		wx.Panel.__init__(self, parent, -1)
		
		self.xml = xmlstr
		self.lastXPath = ''

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


		bottomPanel = wx.Panel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

		xpathLabel = wx.StaticText(bottomPanel, -1, "XPath")
		self.xpath = wx.TextCtrl(bottomPanel)
#		self.xpath.SetEditable(False)
		self.filter = wx.Button(bottomPanel, -1, 'Filter')
		self.copy = wx.Button(bottomPanel, -1, 'Copy To Clipboard')



		leftBox = wx.BoxSizer(wx.VERTICAL)
		leftBox.Add(self.tree, 1, wx.EXPAND)
		leftBox.Add(wx.StaticText(leftPanel, label = "Search in tree"), 0, wx.TOP|wx.LEFT, 5)
		leftBox.Add(self.search, 0, wx.EXPAND|wx.ALL, 5)
		leftPanel.SetSizer(leftBox)


		bottomSizer = wx.FlexGridSizer(cols=4, hgap=4, vgap=10)
		bottomSizer.AddGrowableCol(1)
		bottomSizer.Add(xpathLabel, 1, wx.ALIGN_CENTER_VERTICAL)
		bottomSizer.Add(self.xpath, 2, wx.EXPAND)
		bottomSizer.Add(self.filter,3, wx.ALIGN_CENTER_VERTICAL)
		bottomSizer.Add(self.copy,  4, wx.ALIGN_CENTER_VERTICAL)
		bottomPanel.SetSizer(bottomSizer)


		box = wx.BoxSizer(wx.VERTICAL)
		box.Add(self.splitter, 1, wx.EXPAND, 10)
		box.Add(bottomPanel,   0, wx.EXPAND, 10)
		self.SetSizer(box)


		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)

#		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
		self.Bind(wx.EVT_TEXT, self.OnIncrSearch, self.search)        

		self.attr.UpdateXPath = self.UpdateXPath
		self.Bind(wx.EVT_BUTTON, self.OnFilter, self.filter)
		self.Bind(wx.EVT_BUTTON, self.CopyToClipboard, self.copy)

		if xmlstr.strip():
			self.InitXML()


	def InitXML(self, xmlstr = None):
		if xmlstr:
			self.xml = xmlstr
		self.tree.SetXML(self.xml)

	def SetXML(self, xmlstr):
		self.tree.SetXML(xmlstr)

	def OnSelChanged(self, event):
		# TODO: if unselected
		item = event.GetItem()
		if item and item != self.tree.root:
			item = self.tree.GetSelected()
			data = self.tree.GetPyData(item)
			self.attr.SetElement(data)
			self.text.SetValue(data.element.text if data.element.text else '')
			self.UpdateXPath(item)

	def SearchByText(self, keyword):
		keyword = keyword.lower()
		def nodeFilter(node):
			if keyword in node.element.tag.lower():
				return True
			if node.element.text and keyword in node.element.text.lower():
				return True
			for attrib in node.element.attrib.values():
				if keyword in attrib.lower():
					return True
			return False
		self.tree.FilterTree(nodeFilter)

	def SearchByXPath(self, xpath):
		try:
			elements = self.tree.eroot.findall(xpath)
			nodeFilter = lambda node: node.element in elements
		except SyntaxError, e:
			nodeFilter = lambda elements: False
			print e
			raise
		self.tree.FilterTree(nodeFilter)

	def Search(self):
		keyword = self.search.GetValue()
		if keyword:
			if self.textMenuItem.IsChecked():
				self.SearchByText(keyword)
			else:
				self.SearchByXPath(keyword)
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


	def OnFilter(self, event):
		xpath = self.xpath.GetValue()
		if self.lastXPath == xpath:
			self.tree.RestoreTree()
			self.lastXPath = ''
		else:
			self.SearchByXPath(xpath)
			self.lastXPath = xpath

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
		<item/>
	</others>
</list>
'''
	import Test
	Test.TestPanel(XMLPanel, lambda p: p.InitXML(xml))

