
import wx
import Player
import Controller


class ControllersPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		self.list = wx.ListCtrl(self, -1,
				style=wx.LC_LIST 
				#| wx.BORDER_SUNKEN
				| wx.BORDER_NONE
				#| wx.LC_EDIT_LABELS
				#| wx.LC_SORT_ASCENDING
				#| wx.LC_NO_HEADER
				#| wx.LC_VRULES
				#| wx.LC_HRULES
				| wx.LC_SINGLE_SEL
				)
		self.imagelist = wx.ImageList(16, 16)
		self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_NEW, wx.ART_OTHER, (16,16)))
		self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_QUESTION, wx.ART_OTHER, (16,16)))
		self.imagelist.Add(wx.ArtProvider_GetBitmap(wx.ART_REDO, wx.ART_OTHER, (16,16)))

		self.list.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)
		self.list.InsertImageStringItem(0, 'SCRIPT', 0)
		self.list.InsertImageStringItem(1, 'IF', 1)
		self.list.InsertImageStringItem(2, 'LOOP', 2)

		# layout
		import Layout
		Layout.SingleLayout(self, self.list)

		# event binding
		self.list.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnBeginDrag)

		#
		import Repository
		mapping = [
				Repository.register_object(Player.Script),
				Repository.register_object(Controller.If),
				Repository.register_object(Controller.Loop),
				]
		def GetUserData(index):
			return mapping[index]
		self.list.GetUserData = GetUserData

	def OnBeginDrag(self, event):
		item = event.GetItem()
		list = event.GetEventObject()
		c = list.GetUserData(event.Index)
		#TODO: unfinished...
		def DoDragDrop():
			dd = wx.CustomDataObject("xxx")
			dd.SetData(str(c))

			data = wx.DataObjectComposite()
			data.Add(dd)

			dropSource = wx.DropSource(self)
			dropSource.SetData(data)
			result = dropSource.DoDragDrop(wx.Drag_AllowMove)

		wx.CallAfter(DoDragDrop) # can't call dropSource.DoDragDrop here..




if __name__ == '__main__':
	import Test
	Test.TestPanel(ControllersPanel)


