import uno
import unohelper

from com.sun.star.task import XJob
from com.sun.star.ui import XContextMenuInterceptor
from com.sun.star.ui.ContextMenuInterceptorAction import IGNORED, CANCELLED, EXECUTE_MODIFIED, CONTINUE_MODIFIED

from myhelper import MyUnoHelper
from lookup import BopomoLookup
from lookup import get_syllable

import logging

def insertMenuItem(menu, text, command):
    xRootMenuEntry = menu.createInstance("com.sun.star.ui.ActionTrigger")
    xRootMenuEntry.setPropertyValue("Text", text)
    xRootMenuEntry.setPropertyValue("CommandURL", command)
    menu.insertByIndex(0, xRootMenuEntry)


class BopomoContextMenuInterceptor(unohelper.Base, XContextMenuInterceptor):
    def __init__(self, helper):
        self.helper = helper
        filepath = helper.get_package_file( "addons.whale.BopomoAnnotate", "phtab.pkl" )
        self.lookup = BopomoLookup( filepath )

    def insert_menuitem_mark_selected(self, xContextMenu):
        insertMenuItem(xContextMenu, "標註注音符號",
                       "service:addons.whale.BopomoAnnotate.Job?marksel")
        return CONTINUE_MODIFIED

    def insert_menuitem_mark_char(self, xContextMenu, ch):
        for sym in self.lookup.all(ch):
            text = "標註為" + get_syllable(sym)
            command = "service:addons.whale.BopomoAnnotate.Job?markchar=" + str(sym)
            insertMenuItem(xContextMenu, text, command)
        return CONTINUE_MODIFIED

    def notifyContextMenuExecute(self, aEvent):
        xContextMenu = aEvent.ActionTriggerContainer
        if self.helper.has_text_selection():
            return self.insert_menuitem_mark_selected(xContextMenu)

        ch = self.helper.next_char()
        if ch >= 0x4e00 and ch <= 0x9fff:
            return self.insert_menuitem_mark_char(xContextMenu, ch)

        return IGNORED

class BopomoAnnotateRegistrar(unohelper.Base, XJob):
    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, args):
        helper = MyUnoHelper(self.ctx)
        interceptor = BopomoContextMenuInterceptor( helper )
        if helper.is_text_document() and helper.controller():
            helper.controller().registerContextMenuInterceptor(interceptor)


# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation( \
    BopomoAnnotateRegistrar,  # UNO object class
    "addons.whale.BopomoAnnotate.Registrar",  # Implementation name
    ("com.sun.star.task.Job",), )  # List of implemented services
