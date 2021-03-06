import uno
import unohelper

def access_by_name(tuple, name):
    for item in tuple:
        if item.Name == name:
            return item.Value
    return None


class MyUnoHelper:
    def __init__(self, ctx, model = None):
        self.ctx = ctx
        self.desktop = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.model = model

    def document(self):
        if self.model:
            return self.model

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

    def get_package_file(self, package, filename):
        pip = self.ctx.getByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
        url = pip.getPackageLocation(package) + "/" + filename
        return unohelper.fileUrlToSystemPath(url)

    def next_char(self):
        vc = self.cursor()
        ch = 0
        if vc.goRight(1, True) and len(vc.getString())>0:
            ch = ord(vc.getString())

        vc.collapseToStart()
        return ch

    def is_text_document(self):
        return self.document() and self.document().supportsService("com.sun.star.text.TextDocument")

