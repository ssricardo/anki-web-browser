# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Web browser main dialog
# Main GUI component for this addon
# --------------------------------------------------------

import os
import re
import urllib.parse
from typing import List

from PyQt6.QtCore import *
from PyQt6.QtGui import QAction, QIcon, QShortcut, QKeySequence
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import *

from . import CWD
from .browser_context_menu import AwBrowserMenu, StandardMenuOption, DataImportListener
from .browser_engine import AwWebEngine
from .config.main import config_service as cfg
from .core import Feedback
from .exception_handler import exceptionHandler
from .provider_selection import ProviderSelectionController

WELCOME_PAGE = """
    <html>
        <style type="text/css">
            body {
                margin-top: 30px;
                background-color: #F5F5F5;
                color: 003366;
            }

            p {
                margin-bottom: 20px;
            }
        </style>
        <body>   
            <h1>Welcome</h1>
            <hr />

            <div>
                Anki-Web-Browser is installed!
            </div>
            <p>
                Its use is pretty simple.<br />
                It is based on <i>text selecting</i> and <i>context menu</i> (or shortcut). 
                Now it's also possible to use it without selecting a text.
            </p>
            <div>
                Check more details on the <a href="https://github.com/ssricardo/anki-web-browser">documentation</a>
            </div>
        </body>   
    </html>
"""

BLANK_PAGE = """
    <html>
        <style type="text/css">
            body {
                margin-top: 30px;
                background-color: #154c79;
                color: #F5F5F5;
            }            
            a {
                color: #F0F0F0;
            }
            p {
                margin-bottom: 20px;
            }
        </style>
        <body>   
            <h1>Anki Web Browser</h1>
            <hr />

            <div>
                No page is loaded
            </div>
            <p>
                I'm waiting for the next command ;)
            </p>
            <div>
                If you need instructions, check out the add-on <a href="https://github.com/ssricardo/anki-web-browser">documentation</a>
            </div>
        </body>   
    </html>
"""

Qt.Horizontal = Qt.Orientation.Horizontal


def _create_profile(anki_profile, parent_wdg):
    profile_path = os.path.join(CWD, "profile" + anki_profile)
    profile = QWebEngineProfile("my_profile", parent_wdg)
    profile.setPersistentStoragePath(profile_path)
    profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    profile.setHttpCacheMaximumSize(50 * 1024 * 1024)
    return profile

# noinspection PyPep8Naming
class WebBrowserCore(QVBoxLayout):
    """
    Customization and configuration of a web browser to run within Anki
    """

    SINGLETON = None

    _parent = None
    _context = None
    _currentWeb = None
    _rePageProtocol = re.compile("^((http|ftp)s?|file)://")

    providerList = []

    def __init__(self, parent_wdg: QWidget, anki_profile: str):
        super().__init__(parent_wdg)
        self._parent = parent_wdg
        self.setupUI()
        self._setupShortcuts()

        self._profile = _create_profile(anki_profile, parent_wdg)

        self._menuDelegator = AwBrowserMenu(
            [
                StandardMenuOption(
                    "Open in new tab", lambda add: self._openUrl(add, True)
                )
            ]
        )

    @classmethod
    def singleton(cls, parent, sizeConfig: tuple):
        if not cls.SINGLETON:
            cls.SINGLETON = WebBrowserCore(parent, "local", sizeConfig)
        return cls.SINGLETON

    # ======================================== View setup =======================================

    def setupUI(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        # -------------------- Top / toolbar ----------------------
        navtbar = QToolBar("Navigation")
        navtbar.setIconSize(QSize(16, 16))
        self.addWidget(navtbar)

        backBtn = QAction(
            QIcon(os.path.join(CWD, "assets", "arrow-back.png")), "Back", self
        )
        backBtn.setStatusTip("Back to previous page")
        navtbar.addAction(backBtn)
        backBtn.triggered.connect(self._onBack)

        self._forwardBtn = QAction(
            QIcon(os.path.join(CWD, "assets", "arrow-forward.png")),
            "Forward",
            self,
        )
        self._forwardBtn.setStatusTip("Next visited page")
        navtbar.addAction(self._forwardBtn)
        self._forwardBtn.triggered.connect(self._onForward)

        refreshBtn = QAction(
            QIcon(os.path.join(CWD, "assets", "reload.png")), "Reload", self
        )
        refreshBtn.setStatusTip("Reload")
        navtbar.addAction(refreshBtn)
        refreshBtn.triggered.connect(self._onReload)

        self.createProvidersMenu(navtbar)

        newTabBtn = QAction(
            QIcon(os.path.join(CWD, "assets", "plus-signal.png")),
            "New Tab (Ctrl+t)",
            self,
        )
        newTabBtn.setStatusTip("New tab (Ctrl+t)")
        navtbar.addAction(newTabBtn)
        newTabBtn.triggered.connect(lambda: self.add_new_tab())

        self._itAddress = QLineEdit(self._parent)
        self._itAddress.setObjectName("itSite")
        self._itAddress.setStyleSheet("background-color: #555;color: #FFF;")
        self._itAddress.returnPressed.connect(self._goToAddress)
        self._itAddress.textEdited.connect(self._onAddressFocus)
        navtbar.addWidget(self._itAddress)

        cbGo = QAction(
            QIcon(os.path.join(CWD, "assets", "go-icon.png")), "Go", self
        )
        cbGo.setObjectName("cbGo")
        navtbar.addAction(cbGo)
        cbGo.triggered.connect(self._goToAddress)

        self._stopBtn = QAction(
            QIcon(os.path.join(CWD, "assets", "stop.png")), "Stop", self
        )
        self._stopBtn.setStatusTip("Stop loading")
        self._stopBtn.triggered.connect(self._onStopPressed)

        navtbar.addAction(self._stopBtn)

        # -------------------- Center ----------------------

        self._tabs = QTabWidget(self._parent)
        self._tabs.setDocumentMode(True)
        self._tabs.currentChanged.connect(self.current_tab_changed)
        self._tabs.setTabsClosable(True)
        self._tabs.tabCloseRequested.connect(self.close_current_tab)

        self.addWidget(self._tabs)
        # -------------------- Bottom bar ----------------------
        bottomSplitter = QSplitter(Qt.Horizontal)
        bottomSplitter.setStyleSheet("background-color: #F3F3F3")
        bottomSplitter.setFixedHeight(1)
        self.addWidget(bottomSplitter)

        bottomWidget = QWidget(self._parent)
        bottomWidget.setFixedHeight(30)

        bottomLayout = QHBoxLayout(bottomWidget)
        bottomLayout.setObjectName("bottomLayout")
        bottomWidget.setStyleSheet("color: #FFF")

        lbSite = QLabel(bottomWidget)
        lbSite.setObjectName("label")
        lbSite.setText("Context: ")
        lbSite.setFixedWidth(70)
        lbSite.setStyleSheet("font-weight: bold;")
        bottomLayout.addWidget(lbSite)

        self.ctxWidget = QLabel(bottomWidget)
        self.ctxWidget.width = 300
        self.ctxWidget.setStyleSheet("text-align: left;")
        bottomLayout.addWidget(self.ctxWidget)

        self._loadingBar = QProgressBar(bottomWidget)
        self._loadingBar.setFixedWidth(100)
        self._loadingBar.setProperty("value", 100)
        self._loadingBar.setObjectName("loadingBar")
        bottomLayout.addWidget(self._loadingBar)

        self.addWidget(bottomWidget)

        if cfg.getConfig().enableDarkReader:
            AwWebEngine.enableDarkReader()

    def _setupShortcuts(self):
        newTabShort = QShortcut(QKeySequence("Ctrl+t"), self._parent)
        newTabShort.activated.connect(self.add_new_tab)
        closeTabShort = QShortcut(QKeySequence("Ctrl+w"), self._parent)
        closeTabShort.activated.connect(
            lambda: self.close_current_tab(self._tabs.currentIndex())
        )
        providersShort = QShortcut(QKeySequence("Ctrl+p"), self._parent)
        providersShort.activated.connect(lambda: self.newProviderMenu())
        providerNewTab = QShortcut(QKeySequence("Ctrl+n"), self._parent)
        providerNewTab.activated.connect(lambda: self.newProviderMenu(True))
        goForward = QShortcut(QKeySequence("Alt+right"), self._parent)
        goForward.activated.connect(self._onForward)
        goBack = QShortcut(QKeySequence("Alt+left"), self._parent)
        goBack.activated.connect(self._onBack)
        previousTab = QShortcut(QKeySequence("Ctrl+PgUp"), self._parent)
        previousTab.activated.connect(lambda: self.showRelatedTab(-1))
        nextTab = QShortcut(QKeySequence("Ctrl+PgDown"), self._parent)
        nextTab.activated.connect(lambda: self.showRelatedTab(+1))

    # ======================================== Tabs =======================================

    def add_new_tab(self, qurl: QUrl=None, label="Blank"):
        web_view = AwWebEngine(self._parent, self._profile)
        web_view.preLoadPage()
        if qurl:
            web_view.setUrl(qurl)
        web_view.contextMenuEvent = self._menuDelegator.contextMenuEvent
        web_view.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
        )
        web_view.page().loadStarted.connect(self.onStartLoading)
        web_view.page().loadFinished.connect(self.onLoadFinish)
        web_view.page().loadProgress.connect(self.onProgress)
        web_view.page().urlChanged.connect(self.onPageChange)

        idx = self._tabs.addTab(web_view, label)
        self._tabs.setCurrentIndex(idx)
        self._currentWeb = self._tabs.currentWidget()
        self._menuDelegator.setCurrentWeb(self._currentWeb)

        web_view.urlChanged.connect(
            lambda qurl, bwr=web_view: self.update_urlbar(qurl, bwr)
        )

        web_view.loadFinished.connect(self.updateTabTitle(idx, web_view))

    def current_tab_changed(self, i):
        self._currentWeb = self._tabs.currentWidget()
        self._menuDelegator.setCurrentWeb(self._tabs.currentWidget())

        if self._tabs.currentWidget():
            qurl = self._tabs.currentWidget().url()
            self.update_urlbar(qurl, self._tabs.currentWidget())

        self._updateButtons()

    def close_current_tab(self, i):
        Feedback.log("Close current tab with index: %d of %d" % (i, self._tabs.count()))
        if self._tabs.count() < 2:
            if self._currentWeb:
                self._currentWeb.setUrl(QUrl("about:blank"))
                self._currentWeb.setHtml(BLANK_PAGE)
            return

        if self._tabs.currentIndex() == i:
            self._tabs.setCurrentWidget(None)

        self._close_page_at(i)
        self._tabs.removeTab(i)

    def _close_page_at(self, idx: int):
        engine: AwWebEngine = self._tabs.widget(idx)
        engine.page().deleteLater()
        engine.deleteLater()

    def update_urlbar(self, qUrl, browser=None):
        if browser != self._tabs.currentWidget():
            return

        resolved = self._rePageProtocol.match(qUrl.toString())

        if resolved:
            self._itAddress.setText(qUrl.toString())
        else:
            self._itAddress.setText("")
            self._itAddress.setPlaceholderText("https://about:blank/{}")

        self._itAddress.setCursorPosition(0)

    def _onAddressFocus(self):
        if not self._itAddress.text():
            self._itAddress.setText("https://")

    def updateTabTitle(self, index: int, browser: QWebEngineView):
        def fn():
            title = (
                browser.page().title()
                if len(browser.page().title()) < 18
                else (browser.page().title()[:15] + "...")
            )
            self._tabs.setTabText(index, title)

        return fn

    def showRelatedTab(self, index: int):
        if not self._tabs:
            return
        if self._tabs.currentIndex() == 0 and index < 0:
            return
        if self._tabs.currentIndex() == (len(self._tabs) - 1) and index > 0:
            return
        self._tabs.setCurrentIndex(self._tabs.currentIndex() + index)

    # =================================== General control ======================

    def format_target_url(self, website: str, query: str = ""):
        return website.format(urllib.parse.quote(query, encoding="utf8"))

    @exceptionHandler
    def open(self, website: List[str], query: str, clearContext=False):
        """
        Loads a given page with its replacing part with its query, and shows itself
        """

        if clearContext:
            self.clearContext()

        self._context = query
        self._updateContextWidget()

        if len(website) > 0:
            target = self.format_target_url(website[0], query)
            self._openUrl(target)  # first tab

            for ws in website[1:]:
                target = self.format_target_url(ws, query)
                self._openUrl(target, True)

    def _openUrl(self, address: str, newTab=False):
        if self._tabs.count() == 0 or newTab:
            self.add_new_tab(QUrl(address), "Loading...")
        elif self._currentWeb:
            self._currentWeb.setUrl(QUrl(address))

    def clearContext(self):
        if not self._context:
            return
        numTabs = self._tabs.count()
        if numTabs == 0:
            return
        for tb in range(numTabs, 0, -1):
            self.close_current_tab(tb - 1)

        self._context = None
        self._updateContextWidget()

    def onClose(self):
        if self._currentWeb:
            self._currentWeb.setUrl(QUrl("about:blank"))
            self._currentWeb.setHtml(BLANK_PAGE)
            self._currentWeb = None
        for idx in reversed(range(len(self._tabs))):
            self._close_page_at(idx)

    def onStartLoading(self):
        self._stopBtn.setEnabled(True)
        self._loadingBar.setProperty("value", 1)

    def onProgress(self, progress: int):
        self._loadingBar.setProperty("value", progress)

    def onLoadFinish(self, result):
        self._stopBtn.setDisabled(True)
        self._loadingBar.setProperty("value", 100)

    def _updateButtons(self):
        isLoading: bool = self._currentWeb is not None and self._currentWeb.isLoading
        if isLoading is None:
            isLoading = False
        self._stopBtn.setEnabled(isLoading)
        self._forwardBtn.setEnabled(
            self._currentWeb is not None and self._currentWeb.history().canGoForward()
        )

    def _goToAddress(self):
        q = QUrl(self._itAddress.text())
        if q.scheme() == "":
            q.setScheme("https")

        if not self._currentWeb:
            Feedback.showWarn(
                "Inconsistent state found on Web Browser, with code: AWB-Br373"
            )
            self.clearContext()

        self._currentWeb.load(q)
        self._currentWeb.show()

    def onPageChange(self, url):
        if url and url.toString().startswith("http"):
            self._itAddress.setText(url.toString())
        self._forwardBtn.setEnabled(self._currentWeb.history().canGoForward())

    def _onBack(self, *args):
        self._currentWeb.back()

    def _onForward(self, *args):
        self._currentWeb.forward()

    def _onReload(self, *args):
        self._currentWeb.reload()

    def _onStopPressed(self):
        self._currentWeb.stop()

    def welcome(self):
        self.add_new_tab(None)
        self._currentWeb.setHtml(WELCOME_PAGE)
        self._itAddress.setText("about:blank")

    def _updateContextWidget(self):
        self.ctxWidget.setText(self._context)

    # ---------------------------------------------------------------------------------
    def createProvidersMenu(self, parentWidget):
        providerBtn = QAction(
            QIcon(os.path.join(CWD, "assets", "gear-icon.png")),
            "Providers (Ctrl+p)",
            parentWidget,
        )
        providerBtn.setStatusTip("Search with Provider (Ctrl+p)")
        providerBtn.triggered.connect(lambda: self.newProviderMenu())
        parentWidget.addAction(providerBtn)

        multiBtn = QAction(
            QIcon(os.path.join(CWD, "assets", "multi-cogs.png")),
            "Providers in New tab (Ctrl+n)",
            parentWidget,
        )
        multiBtn.setStatusTip("Open providers in new tab (Ctrl+n)")
        multiBtn.triggered.connect(lambda: self.newProviderMenu(True))
        parentWidget.addAction(multiBtn)

    def newProviderMenu(self, newTab=False):
        ctx = ProviderSelectionController()
        callBack = self._reOpenQueryNewTab if newTab else self._reOpenSameQuery
        ctx.showCustomMenu(self._itAddress, callBack)

    @exceptionHandler
    def _reOpenSameQuery(self, website):
        self.open(website, self._context)

    @exceptionHandler
    def _reOpenQueryNewTab(self, website):
        self.add_new_tab()
        self.open(website, self._context)

    # ------------------------------------ Menu ---------------------------------------

    def load(self, qUrl):
        self._openUrl(qUrl)

    #   ----------------- getter / setter  -------------------

    def setFields(self, fieldsDict: dict):
        self._menuDelegator.fields = fieldsDict

    def set_import_listener(self, value: DataImportListener):
        Feedback.log("Set selectionHandler % s" % str(value))
        self._menuDelegator.listener = value

    def setInfoList(self, data: list):
        self._menuDelegator.infoList = tuple(data)


class BrowserContainer:

    def setFields(self, value):
        raise NotImplementedError("Must be override")

    def setInfoList(self, value: List[str]):
        raise NotImplementedError("Must be override")

    def set_import_listener(self, listener):
        raise NotImplementedError("Must be override")

    def open(self, website: List[str], query: str, bringUp=False, clearContext=False):
        raise NotImplementedError("Must be override")

    def format_target_url(self, website: str, query: str = ""):
        raise NotImplementedError("Must be override")