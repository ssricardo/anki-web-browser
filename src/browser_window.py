# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Web browser main dialog
# Main GUI component for this addon
# --------------------------------------------------------

from typing import List

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from .browser_context_menu import AwBrowserMenu, StandardMenuOption, DataImportListener
from .browser_core import WebBrowserCore, BrowserContainer
from .browser_engine import AwWebEngine
from .config.main import config_service as cfg
from .core import Style
from .exception_handler import exceptionHandler

Qt.Horizontal = Qt.Orientation.Horizontal


# noinspection PyPep8Naming
class WebBrowserWindow(QMainWindow, BrowserContainer):
    """
    Customization and configuration of a web browser to run within Anki
    """

    SINGLETON = None
    TITLE = "Anki :: Web Browser Addon"

    _parent = None

    providerList = []

    def __init__(self, parent_wdg: QWidget, anki_profile: str, sizingConfig: tuple):
        # QDialog.__init__(self, None)
        super().__init__(None)
        self._parent = parent_wdg
        self._core = WebBrowserCore(self, anki_profile)
        self.setupUI(sizingConfig)

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
            cls.SINGLETON = WebBrowserWindow(parent, "local", sizeConfig)
        return cls.SINGLETON

    # ======================================== View setup =======================================

    def setupUI(self, widthHeight: tuple):
        self.setWindowTitle(WebBrowserWindow.TITLE)
        self.setWindowFlags(
            Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint
        )
        self.setGeometry(400, 200, widthHeight[0], widthHeight[1])
        self.setMinimumWidth(620)
        self.setMinimumHeight(400)
        self.setStyleSheet(Style.DARK_BG)

        mainLayout = self._core
        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        if cfg.getConfig().browserAlwaysOnTop:
            self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        if cfg.getConfig().enableDarkReader:
            AwWebEngine.enableDarkReader()


    # =================================== General control ======================

    @exceptionHandler
    def open(self, website: List[str], query: str, bringUp=False, clearContext=False):
        self._core.open(website, query, clearContext)

        if bringUp:
            self.show()
            self.raise_()
            self.activateWindow()

    def clearContext(self):
        self._core.clearContext()

    def onClose(self):
        self._core.onClose()
        super().close()

    # TODO: manter context widget no core ou aqui?
    # def _updateContextWidget(self):
    #     self.ctxWidget.setText(self._context)

    def show_welcome(self, content: str):
        self._core.show_content(content)
        self.show()
        self.raise_()
        self.activateWindow()

    def format_target_url(self, website: str, query: str = ""):
        return self._core.format_target_url(website, query)

    # ------------------------------------ Menu ---------------------------------------

    def load(self, qUrl):
        self._core.load(qUrl)

    #   ----------------- getter / setter  -------------------

    def setFields(self, fieldsDict: dict):
        self._core.setFields(fieldsDict)

    def set_import_listener(self, value: DataImportListener):
        self._core.set_import_listener(value)

    def setInfoList(self, data: list):
        self._core.setInfoList(data)
