# A test for GUI components integrated with the framework used
# Uses PyQt4
# Must not be packed within the distributable file

import os
import sys

from aqt.qt import *

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.argv.append("-awb-test")

import src.browser as brw
from src.result_handler import ResultHandler
from tests.anki_mocks_test import *


def wiki(self):
    print("Load")
    self.load(QUrl("https://en.wikipedia.org"))


def menu(self, evt):
    mn = QMenu(self)
    ac1 = QAction("Unload", mn, triggered=lambda: self.unload())
    mn.addAction(ac1)

    ac2 = QAction("Close", mn, triggered=lambda: self.onClose())
    mn.addAction(ac2)

    ac3 = QAction("Wikipedia", mn, triggered=lambda: wiki(self))
    mn.addAction(ac3)

    ac4 = QAction("Print link", mn, triggered=lambda: print(self.linkUrl()))
    mn.addAction(ac4)

    ac4 = QAction("Print text", mn, triggered=lambda: print(self.selectedText()))
    mn.addAction(ac4)

    action = mn.exec(self.mapToGlobal(evt.pos()))


# browser.AwBrowser.contextMenuEvent = menu


def onSelected(field, value, isLink):
    print("Field {} (link? {}): {}".format(field, isLink, value))


if __name__ == "__main__":
    print("Running Qt App")
    app = QApplication(sys.argv)
    web = brw.AwBrowser(None, (800, 500))

    rHandler = ResultHandler(TestEditor(), TestNote())
    rHandler.handle_selection = onSelected

    web.setResultHandler(rHandler)
    web.setFields({0: 'Front', 1: 'Other', 2: 'Example'})
    web.open(['https://images.google.com/?q={}'], 'my app test')
    web.show()
    sys.exit(app.exec())
