# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Optional

from aqt.qt import *

from .core import Feedback, Label

MediaTypeImage = QWebEngineContextMenuRequest.MediaType.MediaTypeImage

class StandardMenuOption:
    def __init__(self, name: str, fn):
        self.name = name
        self.fn = fn


class DataImportListener(ABC):

    @abstractmethod
    def handle_selection(self, field: int, value: any, isLink: bool):
        pass

# noinspection PyPep8Naming
class AwBrowserMenu:
    """
    Manages context menu, considering whether options should enabled and actions
    """

    infoList = tuple()
    fields: dict = {}
    listener: Optional[DataImportListener] = None
    _lastAssignedField = None

    def __init__(self, defaultOptions: List[StandardMenuOption]):
        self._web = None
        self.generationOptions = defaultOptions

    def setCurrentWeb(self, webReference: QWebEngineView):
        self._web = webReference

    def _makeMenuAction(self, field, value, isLink):
        """
        Creates correct operations for the context menu selection.
        Only with lambda, it would repeat only the last element
        """

        def _processMenuSelection():
            self._lastAssignedField = field
            self.listener.handle_selection(field, value, isLink)

        return _processMenuSelection

    def contextMenuEvent(self, evt):
        """
        Handles the context menu in the web view.
        Shows and handle options (from field list), only if in edit mode.
        """

        if not (self.fields and self.listener):
            Feedback.log(
                "No fields assigned"
                if not self.fields
                else "No selectionHandler assigned"
            )
            return self.createInfoMenu(evt)

        isImageLink = False
        value = None
        if self._web.selectedText():
            isImageLink = False
            value = self._web.selectedText()
        else:
            if self._contextMenuRequest().mediaType() == MediaTypeImage and self._contextMenuRequest().mediaUrl():
                isImageLink = True
                value = self._contextMenuRequest().mediaUrl()
                Feedback.log('Link: ' + value.toString())
                Feedback.log('toLocal: ' + value.toLocalFile())

        if not value:
            Feedback.log("No value")
            return self.createInfoMenu(evt)

        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            if self._assignToLastField(value, isImageLink):
                return

        self.createCtxMenu(value, isImageLink, evt)

    def _contextMenuRequest(self):
        if qtmajor == 5:
            return self._web.page().contextMenuData()
        elif qtmajor == 6:
            return self._web.lastContextMenuRequest()
        else:
            raise RuntimeError("unkown qt version")

    def createCtxMenu(self, value, isImageLink: bool, evt):
        """Creates and configures the menu itself"""

        m = QMenu(self._web)
        m.addAction(QAction("Copy", m, triggered=lambda: self._copy(value)))
        if isImageLink:
            Feedback.log("isLink!")
            for op in self.generationOptions:
                m.addAction(QAction(op.name, m, triggered=lambda: op.fn(value)))
            m.addSeparator()

        labelAct = QAction(Label.BROWSER_ASSIGN_TO, m)
        labelAct.setDisabled(True)
        m.addAction(labelAct)
        m.setTitle(Label.BROWSER_ASSIGN_TO)
        for index, label in self.fields.items():
            act = QAction(
                label, m, triggered=self._makeMenuAction(index, value, isImageLink)
            )
            m.addAction(act)

        action = m.exec(self._web.mapToGlobal(evt.pos()))

    def createInfoMenu(self, evt):
        """Creates and configures a menu with only some information"""

        m = QMenu(self._web)
        linkUrl = self._contextMenuRequest().linkUrl()
        if linkUrl and len(self.generationOptions) > 0:
            for op in self.generationOptions:
                m.addAction(QAction(op.name, m, triggered=lambda: op.fn(linkUrl)))
            m.addSeparator()

        for item in self.infoList:
            act = QAction(item)
            act.setEnabled(False)
            m.addAction(act)

        action = m.exec(self._web.mapToGlobal(evt.pos()))

    def _copy(self, value):
        if not value:
            return
        clip = QApplication.clipboard()
        clip.setText(value if isinstance(value, str) else value.toString())

    def _assignToLastField(self, value, isLink) -> bool:
        """Tries to set the new value to the same field used before, if set..."""

        if self._lastAssignedField:
            if self._lastAssignedField in self.fields:
                self.listener.handle_selection(self._lastAssignedField, value, isLink)
                return True
            else:
                self._lastAssignedField = None
        return False
