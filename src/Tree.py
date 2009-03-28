
import wx
import sys

class Tree(wx.TreeCtrl):
	def __init__(self, parent, multiple = False):
		style = (wx.TR_DEFAULT_STYLE
				 #wx.TR_HAS_BUTTONS
				 | wx.TR_EDIT_LABELS
				 #| wx.TR_MULTIPLE
				 | wx.TR_HIDE_ROOT
				 | wx.TR_HAS_VARIABLE_ROW_HEIGHT)
		if multiple:
			style |= wx.TR_MULTIPLE
		self.multiple = multiple

		wx.TreeCtrl.__init__(self, parent, style = style)
		self.root = self.AddRoot("You can't see me:)")
		self.SetPyData(self.root, None)


		self.iconSize = (16, 16) if sys.platform != 'linux2' else (24, 24)

	def SetIcons(self, icons, iconSize = None):
		if iconSize:
			self.iconSize = iconSize
		self.icons = {}
		iconList = wx.ImageList(*self.iconSize)
		for kind, icon in icons.items():
			if isinstance(icon, list) or isinstance(icon, tuple):
				self.icons[kind] = (iconList.Add(icon[0]), iconList.Add(icon[1]))
			else:
				self.icons[kind] = (iconList.Add(icon),) * 2
		self.SetImageList(iconList)
		self.iconList = iconList

	def SetNode(self, node, data):
		self.SetPyData(node, data)
		icons = self.icons[data.__class__]
		self.SetItemImage(node, icons[0], wx.TreeItemIcon_Normal)
		self.SetItemImage(node, icons[1], wx.TreeItemIcon_Expanded)

	def AddNode(self, parent, data):
		node = self.AppendItem(parent, data.label)
		self.SetNode(node, data)
		return node

	def AddTree(self, parent, data):
		node = self.AddNode(parent, data)
		if hasattr(data, 'childern'):
			for c in data.childern:
				self.AddTree(node, c)
			self.Expand(node)
		return node

	def InsertNode(self, parent, prev, data):
		node = self.InsertItem(parent, prev, data.label)
		self.SetNode(node, data)
		return node

	def InsertTree(self, parent, prev, data):
		node = self.InsertNode(parent, prev, data)
		if hasattr(data, 'childern'):
			for c in data.childern:
				self.AddTree(node, c)
			self.Expand(node)
		return node

	def SelectedData(self):
		return self.GetPyData(self.GetSelected())

	def SelectedDatas(self):
		return map(self.GetPyData, self.GetSelections())

	def GetSelected(self):
		if self.multiple:
			all = self.GetSelections()
			return all[0] if all else None
		else:
			return self.GetSelection()
	def GetAllSelected(self):
		if self.multiple:
			return self.GetSelections()
		else:
			return [self.GetSelection()]


if __name__ == '__main__':
	class P(wx.Panel):
		def __init__(self, parent):
			wx.Panel.__init__(self, parent, -1)
			self.tree = Tree(self, True)
			import Layout
			Layout.SingleLayout(self, self.tree)
			self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
		def OnSelChangedBad(self, event):
			item = event.GetItem()
			data = self.tree.GetPyData(item)
			print data
		def OnSelChangedGood(self, event):
			nodes = self.tree.GetAllSelected()
			if len(nodes) != 1:
				return
			item = event.GetItem()
			data = self.tree.GetPyData(nodes[0])
			print data
		def OnSelChangedVeryGood(self, event):
			item = event.GetItem()
			if item:
				data = self.tree.GetPyData(item)
				print data
		OnSelChanged = OnSelChangedVeryGood
	class Data:
		def __init__(self, label = 'new'):
			self.label = label
	def loadNodes(p):
		tree = p.tree
		icon = wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, (16, 16))
		tree.SetIcons({Data: icon})
		tree.AddNode(tree.root, Data('1'))
		n = tree.AddNode(tree.root, Data('2'))
		tree.AddNode(tree.root, Data('3'))
		tree.AddNode(tree.root, Data('4'))
		tree.AddNode(n, Data('x'))
	import Test
	Test.TestPanel(P, loadNodes)

