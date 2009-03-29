

import wx

def OverwriteConfirm(parent, path, title = "Save Confirmation"):
	dialog = wx.MessageDialog(parent, 'Do you want to overwrite %s?' % path,
			title,
			wx.YES_NO | wx.ICON_WARNING
			)
	selection = dialog.ShowModal()
	dialog.Destroy()
	return selection == wx.ID_YES

def SaveFile(parent, fileType, fileExt, title = "Save file as ..."):
	path = None

	wildcard = "%s (*.%s)|*.%s|All files (*.*)|*.*" % (fileType, fileExt, fileExt)
	dialog = wx.FileDialog(
			parent, message=title, defaultDir="",
			defaultFile="", wildcard=wildcard, style=wx.SAVE
			)
	dialog.SetFilterIndex(0)
	if dialog.ShowModal() == wx.ID_OK:
		path = dialog.GetPath()
	dialog.Destroy()
	if not path:
		return

	# Give a warning if file exists
	import os.path
	if os.path.exists(path):
		if not OverwriteConfirm(parent, path):
			return

	return path


def OpenFile(parent, fileType, fileExt, title = "Open File"):
	path = None

	wildcard = "%s (*.%s)|*.%s|All files (*.*)|*.*" % (fileType, fileExt, fileExt)
	dialog = wx.FileDialog(
			parent, message=title, defaultDir="",
			defaultFile="", wildcard=wildcard, style=wx.OPEN
			)
	dialog.SetFilterIndex(0)
	if dialog.ShowModal() == wx.ID_OK:
		path = dialog.GetPath()
	dialog.Destroy()

	return path


