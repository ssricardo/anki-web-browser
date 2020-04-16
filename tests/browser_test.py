# Testing code for browser module

import unittest
import sys
from anki_mocks_test import *
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

import src.browser
from src.browser import AwBrowser
from src.browser_engine import AwWebEngine
from src.browser_context_menu import AwBrowserMenu
from PyQt5.QtWidgets import QMenu, QApplication, QMainWindow
from PyQt5.QtCore import QPoint
from src.core import Feedback

from src import exception_handler
exception_handler.RAISE_EXCEPTION = True

def testLog(*args, **vargs):
    print(args, vargs)

Feedback.log = testLog

class FakeBrowser:

    def page(self):        
        def currentFrame(self):
            def hitTestContent(self, evt):
                pass
            return self
        return self

class FakeEvent:
    def pos(self):
        return QPoint()


class Tester(unittest.TestCase):

    winSize = (500, 300)

    def setUp(self) -> None:
        #
        pass

    def test_open(self):
        global mw
        b = AwBrowser(None, self.winSize)
        b.open('localhost/search?', 'ricardo')

    def test_clearContext(self):
        global mw
        b = AwBrowser(None, self.winSize)
        b.clearContext()

    def customSelected(self):
        return 'Selecionado!'

    # TODO goto menu test
    def test_repeatableAction(self):
        bm = AwBrowserMenu([])
        bm._fields = [
            {'name': 'Test'},
            {'name': 'Item2'}
        ]
        bm.selectionHandler = lambda a, b, c: print(a, b, c)

        self.assertFalse(bm._assignToLastField('Novo', False))
        menuFn = bm._makeMenuAction(bm._fields[1], 'Test', False)
        menuFn()
        self.assertTrue(bm._assignToLastField('Novo', False))

    def test_close(self):
        b = AwBrowser(None, self.winSize)
        b.onClose()

    def test_installPage(self):
        pass

#   ---------------------- browser engine -------------------
    def test_onContextMenu(self):
        bm = AwBrowserMenu([])
        bm.setCurrentWeb(MockWebEngine())
        bm.contextMenuEvent(FakeEvent())

    def test_textSelection(self):
        bm = AwBrowserMenu([])
        engine = MockWebEngine()
        bm.setCurrentWeb(engine)
        bm._fields = {
            'name': 'Test',
            'name': 'Item2'
        }
        bm.selectionHandler = lambda a, b, c: print(a, b, c)
        engine.selectedText = self.customSelected
        bm.contextMenuEvent(FakeEvent())


if __name__ == '__main__':

    app = QApplication(sys.argv)
    if '-view' in sys.argv:
        sys.argv.append("--disable-web-security")
        main = QMainWindow()
        view = AwBrowser(main, (800, 400))
        view.setFields({0: 'Example', 1: 'Other'})
        view.setInfoList(['No action available'])

        def handlerFn(f, v, l):
            print('Field: %s' % (f))
            print('Link/Value: %s / %s' % (l, v))

        view.setSelectionHandler(handlerFn)
        view.open('https://www.google.com/search?tbm=isch&tbs=isz:i&q={}', 'calendar', True)
        sys.exit(app.exec_())
    else:
        sys.exit(unittest.main())

