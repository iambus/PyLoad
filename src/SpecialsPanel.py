
import wx
from Special import Special
import Controller
import Player
import Record

import Logger
log = Logger.getLogger()

class MyDropTarget(wx.PyDropTarget):
	def __init__(self, panel):
		wx.PyDropTarget.__init__(self)
		self.panel = panel
		self.tree = self.panel.tree

		self.data = wx.CustomDataObject("xxx")
		self.SetDataObject(self.data)


	def OnEnter(self, x, y, d):
		return d

	def OnLeave(self):
		pass

	def OnDrop(self, x, y):
		return True

	def OnDragOver(self, x, y, d):
		return d


	def OnData(self, x, y, d):
		if not self.GetData():
			return d

		item, flags = self.tree.HitTest((x,y))
		if flags & wx.TREE_HITTEST_NOWHERE:
			log.debug('no place to drop')
			return d

		self.panel.DropData(item, self.data.GetData())
#		bits = {
#				wx.TREE_HITTEST_ABOVE : 'wx.TREE_HITTEST_ABOVE',
#				wx.TREE_HITTEST_BELOW : 'wx.TREE_HITTEST_BELOW',
#				wx.TREE_HITTEST_NOWHERE : 'wx.TREE_HITTEST_NOWHERE',
#				wx.TREE_HITTEST_ONITEMBUTTON : 'wx.TREE_HITTEST_ONITEMBUTTON',
#				wx.TREE_HITTEST_ONITEMICON : 'wx.TREE_HITTEST_ONITEMICON',
#				wx.TREE_HITTEST_ONITEMINDENT : 'wx.TREE_HITTEST_ONITEMINDENT',
#				wx.TREE_HITTEST_ONITEMLABEL : 'wx.TREE_HITTEST_ONITEMLABEL',
#				wx.TREE_HITTEST_ONITEMRIGHT : 'wx.TREE_HITTEST_ONITEMRIGHT',
#				wx.TREE_HITTEST_ONITEMSTATEICON : 'wx.TREE_HITTEST_ONITEMSTATEICON',
#				wx.TREE_HITTEST_TOLEFT : 'wx.TREE_HITTEST_TOLEFT',
#				wx.TREE_HITTEST_TORIGHT : 'wx.TREE_HITTEST_TORIGHT',
#		}
#		print bits[flags]

		return d  



class SpecialsTree(wx.TreeCtrl):
	def __init__(self, parent):
		wx.TreeCtrl.__init__(self, parent, 
				style =
				wx.TR_DEFAULT_STYLE
				#wx.TR_HAS_BUTTONS
				| wx.TR_EDIT_LABELS
				#| wx.TR_MULTIPLE
				| wx.TR_HIDE_ROOT
				| wx.TR_HAS_VARIABLE_ROW_HEIGHT
				)
	def SelectedData(self):
		return self.GetPyData(self.GetSelection())

class SpecialsPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		
		self.InitTree()
		self.AppendNewSpecial()
		self.AppendNewSpecial()

		self.SetDropTarget(MyDropTarget(self))
	
		# layout
		import Layout
		Layout.SingleLayout(self, self.tree)

		# bindings
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
		self.onSelChangedCallback = None


	def InitTree(self):
		self.tree = SpecialsTree(self)

		iconSize = (16,16)
		iconList = wx.ImageList(iconSize[0], iconSize[1])

		self.specialIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.specialOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize))

		self.recordIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.recordOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize))

		self.pageIcon       = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, iconSize))
		self.pageOpenIcon   = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, iconSize))
		self.hitIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, iconSize))

		self.scriptIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_NEW, wx.ART_OTHER, iconSize))
		self.ifIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_QUESTION,      wx.ART_OTHER, iconSize))
		self.ifOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, iconSize))
		self.loopIcon     = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_REDO,      wx.ART_OTHER, iconSize))
		self.loopOpenIcon = iconList.Add(wx.ArtProvider_GetBitmap(wx.ART_REDO, wx.ART_OTHER, iconSize))

		self.tree.SetImageList(iconList)
		self.iconList = iconList
		self.root = self.tree.AddRoot("All Specials")
		self.tree.SetPyData(self.root, None)
		self.tree.SetItemImage(self.root, self.specialIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(self.root, self.specialOpenIcon, wx.TreeItemIcon_Expanded)

	def OnSelChanged(self, event):
		self.item = event.GetItem()
		data = self.tree.GetPyData(self.item)
		if self.onSelChangedCallback:
			self.onSelChangedCallback(data)

	def AppendNewSpecial(self):
		specialItem = self.tree.AppendItem(self.root, "sp1")
		self.tree.SetPyData(specialItem, Special())
		self.tree.SetItemImage(specialItem, self.specialIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(specialItem, self.specialOpenIcon, wx.TreeItemIcon_Expanded)

	def DropData(self, item, data):
		itemData = self.tree.GetPyData(item)

		# find a place to insert
		if not (isinstance(itemData, Special) or isinstance(itemData, Controller.Controller)):
			item = self.tree.GetItemParent(item)
			itemData = self.tree.GetPyData(item)
			if not (isinstance(itemData, Special) or isinstance(itemData, Controller.Controller)):
				log.debug('no place to insert')
				return

		import Repository
		data = Repository.lookup(data)
		import inspect
		if inspect.isclass(data):
			data = data()
			self.InsertController(item, data)
		else:
			self.UseRecord(item, data)

	def InsertController(self, item, controller):
		itemData = self.tree.GetPyData(item)
		itemData.add_child(controller)

		subItem = self.tree.AppendItem(item, str(controller.__class__))
		self.tree.SetPyData(subItem, controller)

		icon = None
		if isinstance(controller, Player.Script):
			icon = self.scriptIcon
		elif isinstance(controller, Controller.If):
			icon = self.ifIcon
		elif isinstance(controller, Controller.Loop):
			icon = self.loopIcon
		self.tree.SetItemImage(subItem, icon, wx.TreeItemIcon_Normal)

		self.tree.Expand(item)


	def UseRecord(self, item, data):
		log.debug('use record')
		parentdata = self.tree.GetPyData(item)
		parentdata.add_child(data)

		if isinstance(data, Record.Record):
			self.InsertRecord(item, data)
		elif isinstance(data, Record.Page):
			self.InsertPage(item, data)
		elif isinstance(data, Record.Hit):
			self.InsertHit(item, data)
		else:
			assert False, 'Unknown type'

		self.tree.Expand(item)

	def InsertRecord(self, item, r):
		recordItem = self.tree.AppendItem(item, "%s" % r.label)
		self.tree.SetPyData(recordItem, r)
		self.tree.SetItemImage(recordItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(recordItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for p in r.pages:
			self.InsertPage(recordItem, p)

		self.tree.Expand(recordItem)

	def InsertPage(self, item, p):
		pageItem = self.tree.AppendItem(item, p.path)
		self.tree.SetPyData(pageItem, p)
		self.tree.SetItemImage(pageItem, self.recordIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(pageItem, self.recordOpenIcon, wx.TreeItemIcon_Expanded)

		for h in p.hits:
			self.InsertHit(pageItem, h)

		self.tree.Expand(pageItem)

	def InsertHit(self, item, h):
		hitItem = self.tree.AppendItem(item, h.label)
		self.tree.SetPyData(hitItem, h)
		self.tree.SetItemImage(hitItem, self.hitIcon, wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(hitItem, self.hitIcon, wx.TreeItemIcon_Selected)

		self.tree.Expand(hitItem)

if __name__ == '__main__':
	import Test
	Test.TestPanel(SpecialsPanel)

