# -*- coding: utf-8 -*-
import uno
import unohelper

from com.sun.star.task import XJob
from com.sun.star.task import XJobExecutor
from com.sun.star.ui import XContextMenuInterceptor
from com.sun.star.ui.ContextMenuInterceptorAction import IGNORED,CANCELLED,EXECUTE_MODIFIED,CONTINUE_MODIFIED

import sys
import pickle
import logging

logging.basicConfig(filename='/tmp/bpm.txt',level=logging.DEBUG)

def logException(name , e):
    logging.debug(name+"Exception " + str(type(e)) + " message " + str(e) + " args " + str(e.args))

def insertMenuItem( menu, text, command ):
    xRootMenuEntry = menu.createInstance ( "com.sun.star.ui.ActionTrigger" )
    xRootMenuEntry.setPropertyValue( "Text",  text )
    xRootMenuEntry.setPropertyValue( "CommandURL",  command )
    menu.insertByIndex ( 0, xRootMenuEntry )

def hasSelection( selection ):
    if selection is None:
        return False
    if not selection.supportsService("com.sun.star.text.TextRanges"):
        return False
    count = selection.getCount()
    if count == 0:
        return False
    if count == 1:
        oneSel = selection.getByIndex(0)
        return len(oneSel.getString()) > 0
    return True

class BopomoAnnotateJob(unohelper.Base, XJobExecutor,XJob,XContextMenuInterceptor):
    def __init__(self, ctx):
        # store the component context for later use
        self.ctx = ctx
        self.dictionary = {}
        # Retrieve the desktop object
        self.desktop = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)

    def document(self):
        return self.desktop.getCurrentComponent()

    def controller( self ):
        return self.document().getCurrentController()

    def cursor( self ):
        return self.controller().getViewCursor()

    def notifyContextMenuExecute( self, aEvent ):
        try:
            xContextMenu = aEvent.ActionTriggerContainer
            if hasSelection(self.controller().getSelection()):
                insertMenuItem( xContextMenu ,"標註注音符號",  "service:addons.whale.BopomoAnnotate.Job?marksel" )
                return CONTINUE_MODIFIED

            vc = self.cursor()
            if not vc.goRight(1, True):
                return IGNORED

            dictionary = self.getDictionary()
            ch = ord(vc.getString())
            vc.collapseToStart()

            if not ( ch >= 0x4e00 and ch <= 0x9fff): 
                return IGNORED

            for sym in dictionary[ch]:
                text = "標註為" + get_syllable(sym)
                command ="service:addons.whale.BopomoAnnotate.Job?markchar="+str(sym) 
                insertMenuItem( xContextMenu ,text, command)
        except Exception as e:
            logException("notifyContextMenuExecute()", e)
            return CONTINUE_MODIFIED
        return CONTINUE_MODIFIED

    def registerContextMenuInterceptor(self):	
        try:
            self.controller().registerContextMenuInterceptor(self)
        except Exception as e:
            logException("registerContextMenuInterceptor()", e)

    def getDictionary(self):
        if not self.dictionary:
            try:
                logging.debug("Loading phtab.pkl")
                pip = self.ctx.getByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
                url = pip.getPackageLocation("addons.whale.BopomoAnnotate") + "/phtab.pkl"
                loc = unohelper.fileUrlToSystemPath(url)
                file = open(loc,'rb')                
                self.dictionary = pickle.load(file)
                file.close()
            except Exception as e:
                logException("getDictionary()", e)

        return self.dictionary


    def mark_textrange(self, oneSel):
        if not oneSel.supportsService("com.sun.star.text.TextRange"):
            return

        oText = oneSel.getText()
        oEnums = oneSel.createEnumeration()
        while oEnums.hasMoreElements():
            oPara = oEnums.nextElement()
            if not oPara.supportsService("com.sun.star.text.Paragraph"):
                continue
            oCursor = oText.createTextCursorByRange(oneSel.getStart())
            if oText.compareRegionStarts(oPara,oneSel)>0:
                oCursor = oText.createTextCursorByRange(oneSel.getStart())
            else:
                oCursor = oText.createTextCursorByRange(oPara.getStart())

            if oText.compareRegionEnds(oPara,oneSel) <0:
                oEnd = oText.createTextCursorByRange(oneSel.getEnd())
            else:
                oEnd = oText.createTextCursorByRange(oPara.getEnd())

            while oCursor.goRight(1, True) and oText.compareRegionEnds(oCursor,oEnd) >= 0:
                ch = ord(oCursor.String)
                if ch >= 0x4e00 and ch <= 0x9fff:
                    dictionary = self.getDictionary()
                    oCursor.RubyText = get_syllable(dictionary[ ch][0])
                oCursor.collapseToEnd()

    def markChar(self, sym):
        vc = self.cursor()
        if vc.goRight(1, True):
            vc.RubyText = get_syllable(sym)
            vc.collapseToStart()

    def markSelectedText(self): 
        selection = self.controller().getSelection()
        if not hasSelection(selection):
            return

        undo = self.document().UndoManager
        undo.enterUndoContext("BopomoAnnotate")
        for i in range(selection.getCount()):
            self.mark_textrange(selection.getByIndex(i))

        undo.leaveUndoContext()

    def execute(self, args):
        try:
            if self.document().supportsService("com.sun.star.text.TextDocument"):
                self.registerContextMenuInterceptor()
        except Exception as e:
            logException("execute()", e)
 
    def trigger(self, args):
        try:
        # Retrieve the desktop object
            if args.startswith( "marksel" ):
                self.markSelectedText()
            elif args.startswith("markchar="):
                self.markChar(int(args.split("=")[1]))
            else:
                logging.debug("trigger() other")
        except Exception as e:
            logException("trigger()", e)


def get_syllable(ch):
    #5bit
    InitialConsonants= "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ"
    #2bit
    Medials="ㄧㄨㄩ"
    #4bit
    FinalConsonants="ㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ"
    #3bit
    Tones="ˊˇˋ˙"
    ic = ch & 0b11111
    m = ( ch >> 5 ) & 0b11
    fc = ( ch >> 7) & 0b1111
    t = (ch >> 11) & 0b111
    s = ''
    #print("%d %d %d %d" % (ic,m,fc,t))
    if t==4:
        s += Tones[3];
    if ic!=0 and ic<=len(InitialConsonants):
        s += InitialConsonants[ic-1]
    if m!=0 and m<=len(Medials):
        s += Medials[m-1]
    if fc!=0 and fc<=len(FinalConsonants):
        s += FinalConsonants[fc-1]
    if t!=0 and t<=len(Tones)-1:
        s += Tones[t-1]
    return s


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation( \
        BopomoAnnotateJob,                            # UNO object class
        "addons.whale.BopomoAnnotate.Job",                   # Implementation name
        ("com.sun.star.task.Job",),)                  # List of implemented services
