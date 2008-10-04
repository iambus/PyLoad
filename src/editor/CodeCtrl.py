
import re
import wx
import wx.stc as stc


import ConfigUtil

#----------------------------------------------------------------------

demoText = """\
## Python comment
Number = 12345
String = 'abcde'
String = "abcde and long ................................................................................................ and long"
String = \"\"\"
everything
\"\"\"
Dict = {1:'hehe'}
List = [1, 2, 3]
Tuple = (1, 2, 3)

debug = debug
def F(V):
    for a, b in k.items():
        len(a)

## Python comment
"""

#----------------------------------------------------------------------
colorpath = 'colors/ps_color.colors'
configdict = None

colorpathes = ['colors/ps_color.colors',
               'ps_color.colors',
               'editor/colors/ps_color.colors',
               'colors/default.colors',
               'default.colors',
               'editor/colors/default.colors']
import os.path
for p in colorpathes:
    if os.path.exists(p):
        colorpath = p
        break
#colorpath = 'editor/colors/default.colors'

def SetColorPath(path):
    global colorpath
    colorpath = path

def SetConfigDict(d):
    global configdict
    configdict = d

#----------------------------------------------------------------------

class CodeCtrl(stc.StyledTextCtrl):

    def __init__(self, parent, ID = -1,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, syntax=None):
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        if syntax == None:
            #XXX: why syntax.default is not working?
            #import syntax.default as syntax
            import syntax.python as syntax
        self.LoadSyntax(syntax)

        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)


        self.SetViewWhiteSpace(False)
        #self.SetBufferedDraw(False)
        #self.SetViewEOL(True)
        #self.SetEOLMode(stc.STC_EOL_CRLF)
        #self.SetUseAntiAliasing(True)
        
        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(78)


        self.SetIndent(4)               # Proscribed indent size for wx
        self.SetIndentationGuides(True) # Show indent guides
        self.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
        self.SetTabIndents(True)        # Tab key indents
        self.SetTabWidth(4)             # Proscribed tab size for wx
        #self.SetUseTabs(False)

        # show line numbers
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginSensitive(1, True)
        self.SetMarginWidth(1, 40)

        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)

        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from
        # Scintilla sample property files.

        self.StyleClearAll()  # Reset all to be like the default

        self.LoadColors()


    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == self.syntax.OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == self.syntax.OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            #pt = self.PointFromPosition(braceOpposite)
            #self.Refresh(True, wxRect(pt.x, pt.y, 5,5))
            #print pt
            #self.Refresh(False)


    def LoadColors(self):
        global configdict
        if configdict == None:
            configdict = ConfigUtil.LoadConfigDictFromFile(colorpath)

        lang = re.compile(r'^[0-9A-Z]+$')
        style = re.compile(r'^[0-9A-Z_]+$')
        for k, v in configdict.items():
            if lang.match(k):
                k = self.syntax.Prefix + k
                if not hasattr(stc, k):
                    #print "Warning: Can't find %s" % k
                    continue
                k = getattr(stc, k)
                self.StyleSetSpec(k, v)
            elif style.match(k):
                k = getattr(stc, k)
                self.StyleSetSpec(k, v)
            else:
                pass

        if configdict.has_key('caretforeground'):
            self.SetCaretForeground(configdict['caretforeground'])
        if configdict.has_key('selbackground'):
            self.SetSelBackground(1, configdict['selbackground'])
        if configdict.has_key('selforeground'):
            self.SetSelForeground(1, configdict['selforeground'])

    def LoadSyntax(self, syntax):
        assert syntax != None
        self.syntax = syntax
        self.SetLexer(self.syntax.LEXER)
        self.SetKeyWords(0, " ".join(self.syntax.word))
        self.SetKeyWords(1, " ".join(self.syntax.word2))
        self.SetKeyWords(2, " ".join(self.syntax.word3))
        self.SetKeyWords(3, " ".join(self.syntax.word4))
        self.SetKeyWords(4, " ".join(self.syntax.word5))

    def SetSyntax(self, syntax):
        self.LoadSyntax(syntax)
        #XXX: how to reload all colors?
        self.LoadColors()

    #TODO: support changing colors at runtime
    def SetColors(self, colors):
        raise NotImplementedError('TODO: support changing colors at runtime')

    SetValue = stc.StyledTextCtrl.SetText
    def GetValue(self):
        return self.GetText().replace('\r\n', '\n')

    #------------------------------

    #TODO: match-case
    def SearchText(self, text, forward = True, regex = False):
        if text == '':
            self.CancelSearch()
            return
        fullText = self.GetText()
        selectedText = self.GetSelectedText()
        if not regex:
            if forward:
                start = self.GetSelection()[0]
                if selectedText == text:
                    start += len(selectedText)
                next = fullText.find(text, start)
            else:
                end = self.GetSelection()[1]
                if selectedText == text:
                    end -= len(selectedText)
                next = fullText.rfind(text, 0, end)
            if next != -1:
                self.SetSelection(next, next+len(text))
        else:
            import re
            try:
                regexp = re.compile(text)
            except:
                # Invalid regular expression. Ignore it.
                return
            if forward:
                start = self.GetSelection()[0]
                if regexp.search(selectedText):
                    start += len(selectedText)
                m = regexp.search(fullText, start)
            else:
                end = self.GetSelection()[1]
                if regexp.search(selectedText):
                    end -= len(selectedText)
                # FIXME: '12345', '\d\d\d' should return '345' instead of '123'
                iter = regexp.finditer(fullText, 0, end)
                m = None
                try:
                    while True:
                        m = iter.next()
                except StopIteration:
                    pass
            if m:
                self.SetSelection(m.start(), m.end())

    def HighlightText(self, text):
        raise NotImplementedError("Don't know how to highlight...")

    def CancelSearch(self):
        range = self.GetSelection()
        if range[0] != range[1]:
            self.SetSelection(range[0], range[0])
        #TODO: de-highlight

#----------------------------------------------------------------------

def test():
    import syntax.lua
    import syntax.python
    import syntax.default
    import syntax.xml
    import syntax.html
    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "TestPanel", size = (800, 600))

    p = CodeCtrl(frame)
    p.SetText(demoText)
    #p.SetSyntax(syntax.xml)

    frame.Center()
    frame.Show(True)
    app.MainLoop()

    #import Test
    #Test.TestPanel(CodeCtrl, lambda p: p.SetText(demoText))

if __name__ == '__main__':
    test()


# vim: expandtab:shiftwidth=4:
