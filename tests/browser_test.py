# Testing code for browser module

import pytest
import sys
from tests.anki_mocks_test import *
import os
from PyQt5.QtWidgets import QMenu, QApplication, QMainWindow
from PyQt5.QtCore import QPoint

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
sys.argv.append('-awb-test')

from PyQt5.QtWebEngineWidgets import QWebEngineView
app = QApplication(sys.argv)

from src.browser import AwBrowser
from src.browser_context_menu import AwBrowserMenu
from src.core import Feedback
from src.result_handler import ResultHandler

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

winSize = (500, 300)

def setUp() -> None:
    #
    pass

def test_open():
    global mw
    b = AwBrowser(None, winSize)
    b.open(['localhost/search?'], 'ricardo')

def test_clearContext():
    global mw
    b = AwBrowser(None, winSize)
    b.clearContext()

def customSelected():
    return 'Selecionado!'

# TODO goto menu test
def test_repeatableAction():
    bm = AwBrowserMenu([])
    bm.fields = [
        {'name': 'Test'},
        {'name': 'Item2'}
    ]
    bm.resultHandler = lambda a, b, c: print(a, b, c)

    assert not (bm._assignToLastField('Novo', False))
    menuFn = bm._makeMenuAction(bm.fields[1], 'Test', False)
    menuFn()
    assert (bm._assignToLastField('Novo', False))

def test_close():
    b = AwBrowser(None, winSize)
    b.onClose()

def test_installPage():
    pass

#   ---------------------- browser engine -------------------
@pytest.mark.skip
def test_onContextMenu():
    bm = AwBrowserMenu([])
    bm.setCurrentWeb(MockWebEngine())
    bm.contextMenuEvent(FakeEvent())

def test_textSelection():
    bm = AwBrowserMenu([])
    engine = MockWebEngine()
    bm.setCurrentWeb(engine)
    bm.fields = {
        'name': 'Test',
        'name': 'Item2'
    }
    bm.resultHandler = lambda a, b, c: print(a, b, c)
    engine.selectedText = customSelected
    bm.contextMenuEvent(FakeEvent())

# Only for local tmp test, but test result will fail due to sys.exit
@pytest.mark.skip
def test_integratedView():
    sys.argv.append("--disable-web-security")
    app = QApplication(sys.argv)
    main = QMainWindow()
    view = AwBrowser(main, (900, 600))
    view.setFields({0: 'Example', 1: 'Other'})
    view.setInfoList(['No action available'])

    def handlerFn(f, v, l):
        print('Field: %s' % (f))
        print('Link/Value: %s / %s' % (l, v))

    view.setResultHandler(handlerFn)
    view.open(['https://www.google.com/search?tbm=isch&tbs=isz:i&q={}',
               'https://translate.google.com/#view=home&op=translate&sl=auto&tl=en&text={}'], 'calendar', True)
    sys.exit(app.exec_())


if __name__ == '__main__':

    if '-view' in sys.argv:
        sys.argv.append("--disable-web-security")
        main = QMainWindow()
        view = AwBrowser(main, (800, 400))
        view.setFields({0: 'Example', 1: 'Other'})
        view.setInfoList(['No action available'])

    rHandler = ResultHandler(TestEditor(), TestNote())

    def handlerFn(f, v, l):
        print('Field: %s' % (f))
        print('Link/Value: %s / %s' % (l, v))

    rHandler.handle_selection = handlerFn

    view.setResultHandler(rHandler)
    view.open(['https://www.google.com/search?tbm=isch&tbs=isz:i&q={}'], 'calendar', True)
    sys.exit(app.exec_())

