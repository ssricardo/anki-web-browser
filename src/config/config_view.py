# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QUrl
from PyQt5.Qt import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QPushButton, QApplication, QStyle
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import os
import json

from .main import ConfigHolder

CURDIR = os.path.dirname(os.path.realpath(__file__))


# noinspection PyPep8Naming,PyMethodMayBeStatic
class ConfigView(QDialog):

    def __init__(self, myParent: QWidget):
        self._config = ConfigHolder()

        QDialog.__init__(self, myParent)
        self.setWindowTitle("Anki Web Browser :: Config")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(1080, 600)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        self.setLayout(mainLayout)

        browser = QWebEngineView(self)
        browser.page().loadFinished.connect(self.onLoadFinish)
        browser.setUrl(QUrl.fromLocalFile(os.path.join(CURDIR, "web", "config.html")))
        browser.contextMenuEvent = self.contextMenu
        browser.setZoomFactor(1)
        mainLayout.addWidget(browser)

        widgetActions = QWidget(mainLayout.widget())
        widgetActions.setFixedHeight(50)
        widgetActions.setObjectName("widgetActions")

        btActionsBox = QHBoxLayout(widgetActions)
        btActionsBox.setSpacing(20)
        btActionsBox.setObjectName("btActionsBox")

        btSave = QPushButton(widgetActions)
        btSave.setObjectName("btSave")
        btSave.setText("Save")
        btSave.setFixedSize(150, 35)
        btSave.clicked.connect(lambda: self.onSaveClick())
        btActionsBox.addWidget(btSave)

        btCancel = QPushButton(widgetActions)
        btCancel.setObjectName("btCancel")
        btCancel.setText("Cancel")
        btCancel.setFixedSize(150, 35)
        btCancel.clicked.connect(lambda: self.onCancelClick())
        btActionsBox.addWidget(btCancel)

        btSave.setIcon(self.getIcon(QStyle.SP_DialogApplyButton))
        btCancel.setIcon(self.getIcon(QStyle.SP_DialogCancelButton))

        mainLayout.addWidget(widgetActions)

        self.web = browser

    def getIcon(self, qtStyle):
        return QIcon(QApplication.style().standardIcon(qtStyle))

    def onLoadFinish(self, result):
        self.web.page().runJavaScript('loadConfig(%s)' %
                                      json.dumps(self._config.toDict()))

    def onSaveClick(self):
        jsReadConfig = 'saveAndGetConfig()'

        def storeConfig(cfg):
            conf = ConfigHolder(**cfg)
            if self.save(conf):
                self.close()

        self.web.page().runJavaScript(jsReadConfig, storeConfig)

    def save(self, config: ConfigHolder) -> bool:
        raise Exception("Not implemented")

    def onCancelClick(self):
        self.close()

    def open(self, currentConfig: ConfigHolder) -> None:
        self._config = currentConfig
        self.web.reload()

        self.show()
        self.raise_()
        self.activateWindow()

    def contextMenu(self, event):
        pass
