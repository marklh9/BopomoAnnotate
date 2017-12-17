import uno
import unohelper

class MyUnoHelper:
    def __init__(self, ctx):
        self.ctx = ctx
        self.desktop = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)

    def document(self):
        return self.desktop.getCurrentComponent()

    def controller(self):
        return self.document().getCurrentController()

    def cursor(self):
        return self.controller().getViewCursor()

    def undomanager(self):
        return self.document().UndoManager

    def has_text_selection(self):
        if self.controller() and self.controller().getSelection():
            selection = self.controller().getSelection()

            if not selection.supportsService("com.sun.star.text.TextRanges"):
                return False

            if selection.getCount() == 1:
                return len(selection.getByIndex(0).getString()) > 0

        return False


