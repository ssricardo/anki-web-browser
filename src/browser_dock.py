# -*- coding: utf-8 -*-

# --------------------------------------------------------
# Web browser add-on
# Optional GUI for Browser component
# --------------------------------------------------------

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

from .browser_context_menu import AwBrowserMenu, StandardMenuOption, DataImportListener
from .browser_core import WebBrowserCore, BrowserContainer
from .browser_engine import AwWebEngine
from .config.main import config_service as cfg
from .exception_handler import exceptionHandler

Qt.Horizontal = Qt.Orientation.Horizontal


# noinspection PyPep8Naming
class WebBrowserDock(QDockWidget, BrowserContainer):
    """
    Customization and configuration of a web browser to run within Anki
    """

    TITLE = "Anki :: Web Browser Addon"

    _parent: QMainWindow = None
    providerList = []

    def __init__(self, parent_wdg: QMainWindow, anki_profile: str, sizingConfig: tuple):
        super().__init__(WebBrowserDock.TITLE, parent_wdg)
        self._parent = parent_wdg
        self._core = WebBrowserCore(parent_wdg, anki_profile)
        self.setupUI(sizingConfig)

        self._menuDelegator = AwBrowserMenu(
            [
                StandardMenuOption(
                    "Open in new tab", lambda add: self._openUrl(add, True)
                )
            ]
        )

    @staticmethod
    def new(parent, sizeConfig: tuple):
        return WebBrowserDock(parent, "local", sizeConfig)

    # ======================================== View setup =======================================

    def setupUI(self, widthHeight: tuple):
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.BottomDockWidgetArea)

        main_layout = self._core
        widget = QWidget(self._parent)
        widget.setLayout(main_layout)
        self.setWidget(widget)

        self._parent.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self)
        # self.visibilityChanged.connect(lambda visible: self.onClose() if not visible else None)
        self.hide()

        if cfg.getConfig().enableDarkReader:
            AwWebEngine.enableDarkReader()


    # =================================== General control ======================

    @exceptionHandler
    def open(self, website: List[str], query: str, bringUp=False, clearContext=False):
        self._core.open(website, query, clearContext)
        self.show()

    def clearContext(self):
        self._core.clearContext()

    def onClose(self):
        self._core.onClose()
        super().close()

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
