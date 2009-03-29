
import wx
import sys

class TreeNode:
	def __init__(self, data, children):
		self.data = data
		self.children = children

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

		self.rootDatas = None

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


	def GetLabel(self, data):
		return data.label
	
	def GetChildren(self, data):
		if hasattr(data, 'children'):
			return data.children
		else:
			return []

	def GetType(self, data):
		return data.__class__
	
	def GetIcon(self, data):
		return self.icons[self.GetType(data)]


	# Create nodes

	def SetNode(self, node, data):
		self.SetPyData(node, data)
		icons = self.GetIcon(data)
		self.SetItemImage(node, icons[0], wx.TreeItemIcon_Normal)
		self.SetItemImage(node, icons[1], wx.TreeItemIcon_Expanded)

	def AddNode(self, parent, data):
		node = self.AppendItem(parent, self.GetLabel(data))
		self.SetNode(node, data)
		return node

	def AddTree(self, parent, data):
		node = self.AddNode(parent, data)
		children = self.GetChildren(data)
		if children:
			for c in children:
				self.AddTree(node, c)
			self.Expand(node)
		return node

	def InsertNode(self, parent, prev, data):
		node = self.InsertItem(parent, prev, self.GetLabel(data))
		self.SetNode(node, data)
		return node

	def InsertTree(self, parent, prev, data):
		node = self.InsertNode(parent, prev, data)
		if hasattr(data, 'children'):
			for c in data.children:
				self.AddTree(node, c)
			self.Expand(node)
		return node


	# Filter nodes

	def FilterTree(self, func, weakly = True):
		if self.rootDatas is None:
			self.rootDatas = map(self.GetPyData, self.GetChildrenNodes(self.root))
		self.DeleteChildren(self.root)
		for data in self.rootDatas:
			if weakly:
				self.AddTreeWithWeakFilter(self.root, data, func)
			else:
				self.AddTreeWithFilter(self.root, data, func)

	def AddTreeWithFilter(self, parent, data, func):
		if not func(data):
			return
		node = self.AddNode(parent, data)
		children = self.GetChildren(data)
		if children:
			expand = 0
			for c in children:
				if self.AddTreeWithFilter(node, c, func):
					expand = 1
			if expand:
				self.Expand(node)
		return node

	def AddTreeWithWeakFilter(self, parent, data, func):
		node = self.DataToTreeNode(data)
		node = self.FilterTreeNodeWeakly(node, func)
		if node:
			self.AddTreeNode(parent, node)

	def DataToTreeNode(self, data):
		children = self.GetChildren(data)
		return TreeNode(data, map(self.DataToTreeNode, children))

	def AddTreeNode(self, parent, treeNode):
		node = self.AddNode(parent, treeNode.data)
		children = treeNode.children
		if children:
			for c in children:
				self.AddTreeNode(node, c)
			self.Expand(node)
		return node

	def FilterTreeNode(self, node, func):
		if func(node):
			children = map(lambda n: self.FilterTreeNodeWeakly(n, func), node.children)
			children = filter(lambda n: n, children)
			return TreeNode(node.data, children)


	def FilterTreeNodeWeakly(self, node, func):
		children = map(lambda n: self.FilterTreeNodeWeakly(n, func), node.children)
		children = filter(lambda n: n, children)
		if children or func(node.data):
			return TreeNode(node.data, children)


	def RestoreTree(self):
		if self.rootDatas is None:
			return
		rootDatas = self.rootDatas
		self.rootDatas = None
		self.DeleteChildren(self.root)
		for data in rootDatas:
			self.AddTree(self.root, data)


	# Get selected data

	def SelectedData(self):
		return self.GetPyData(self.GetSelected())

	def SelectedDatas(self):
		return map(self.GetPyData, self.GetAllSelected())

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
			node = self.GetSelection()
			return [node] if node else []

	def GetSelectedRoots(self):
		nodes = self.GetAllSelected()
		if len(nodes) > 1:
			return self.GetMultipleSelectedRoots(self.root)
		else:
			return nodes

	def GetMultipleSelectedRoots(self, node):
		#assert self.multiple
		if node != self.root and self.IsSelected(node):
			return [node]
		else:
			nodes = []
			(child, cookie) = self.GetFirstChild(node)
			while child.IsOk():
				nodes.extend(self.GetMultipleSelectedRoots(child))
				(child, cookie) = self.GetNextChild(node, cookie)
			return nodes

	# Help methods
	def GetChildrenNodes(self, parent):
		children = []
		(child, cookie) = self.GetFirstChild(parent)
		while child.IsOk():
			children.append(child)
			(child, cookie) = self.GetNextChild(parent, cookie)
		return children

	def CanReach(self, child, parent):
		while child != self.root:
			if child == parent:
				return True
			child = self.GetItemParent(child)

	def IndexOf(self, child, parent = None):
		if parent is None:
			parent = self.GetItemParent(child)

		index = 0

		(c, cookie) = self.GetFirstChild(parent)
		while c.IsOk():
			if c == child:
				return index
			index += 1
			(c, cookie) = self.GetNextChild(parent, cookie)
		return -1


# {{{ main
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
# }}}

# vim: foldmethod=marker:
