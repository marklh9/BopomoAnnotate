# -*- coding: utf-8 -*-
import uno
import unohelper
from com.sun.star.task import XJobExecutor

import logging

from lookup import BopomoLookup
from lookup import get_syllable
from myhelper import MyUnoHelper

logging.basicConfig(filename='/tmp/bpm.txt', level=logging.DEBUG)


def logException(name, e):
    logging.debug(name + "Exception " + str(type(e)) + " message " + str(e) + " args " + str(e.args))



class BopomoAnnotateJob(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        # store the component context for later use
        self.ctx = ctx
        filepath = MyUnoHelper( ctx ).get_package_file( "addons.whale.BopomoAnnotate", "phtab.pkl" )
        self.lookup = BopomoLookup( filepath )

    def lookup_one(self,ch):
        return self.lookup.one(ch)

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
            if oText.compareRegionStarts(oPara, oneSel) > 0:
                oCursor = oText.createTextCursorByRange(oneSel.getStart())
            else:
                oCursor = oText.createTextCursorByRange(oPara.getStart())

            if oText.compareRegionEnds(oPara, oneSel) < 0:
                oEnd = oText.createTextCursorByRange(oneSel.getEnd())
            else:
                oEnd = oText.createTextCursorByRange(oPara.getEnd())

            while oCursor.goRight(1, True) and oText.compareRegionEnds(oCursor, oEnd) >= 0:
                ch = ord(oCursor.String)
                if ch >= 0x4e00 and ch <= 0x9fff:
                    oCursor.RubyText = get_syllable(self.lookup.one(ch))
                oCursor.collapseToEnd()

    def mark_char(self, sym):
        vc = self.helper.cursor()
        if vc.goRight(1, True):
            vc.RubyText = get_syllable(sym)
            vc.collapseToStart()

    def mark_selected_text(self):
        if not self.helper.has_text_selection():
            return
        selection = self.helper.controller().getSelection()
        undo = self.helper.undomanager()
        undo.enterUndoContext("BopomoAnnotate")

        for i in range(selection.getCount()):
            self.mark_textrange(selection.getByIndex(i))

        undo.leaveUndoContext()

    def trigger(self, args):
        try:
            self.helper = MyUnoHelper( self.ctx )
            # Retrieve the desktop object
            if args.startswith("marksel"):
                self.mark_selected_text()
            elif args.startswith("markchar="):
                self.mark_char(int(args.split("=")[1]))
            else:
                logging.debug("trigger() other")
        except Exception as e:
            logException("trigger()", e)

# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation( \
    BopomoAnnotateJob,  # UNO object class
    "addons.whale.BopomoAnnotate.Job",  # Implementation name
    ("com.sun.star.task.Job",), )  # List of implemented services
